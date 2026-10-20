import BarcodeQuantModel from "@stock_barcode/models/barcode_quant_model";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(BarcodeQuantModel.prototype, {
    setData() {
        super.setData(...arguments);
        this.pendingLotSelection = null;
    },

    get barcodeInfo() {
        if (this.pendingLotSelection) {
            return {
                class: "scan_lot",
                message: _t(
                    "Select or create a lot for %s",
                    this.pendingLotSelection.product.display_name
                ),
                icon: "barcode",
            };
        }
        return super.barcodeInfo;
    },

    // A product barcode for a tracked product carries no lot. Hold the count
    // line until the user picks or creates one on the main page, so a lot-less
    // quant is never saved (lot_id cannot be set once the quant exists).
    async _processBarcode(barcode) {
        this._scannedTrackedProductWithoutLot = false;
        this._pendingLotQuantity = 1;
        this._deferManualLot = true;
        try {
            await super._processBarcode(barcode);
        } finally {
            this._deferManualLot = false;
        }
        if (this._scannedTrackedProductWithoutLot) {
            this.pendingLotSelection = {
                product: this._scannedTrackedProductWithoutLot,
                quantity: this._pendingLotQuantity || 1,
            };
            this.trigger("update");
        } else if (this.pendingLotSelection && this.scanHistory[0]?.match) {
            this.pendingLotSelection = null;
            this.trigger("update");
        }
    },

    async _parseBarcode(barcode, filters) {
        const result = await super._parseBarcode(barcode, filters);
        this._rememberTrackedProductWithoutLot(result?.product, result);
        return result;
    },

    _retrievePackagingData(barcodeData) {
        const data = super._retrievePackagingData(...arguments);
        this._rememberTrackedProductWithoutLot(
            data.product,
            barcodeData,
            data.quantity
        );
        return data;
    },

    _rememberTrackedProductWithoutLot(product, barcodeData, quantity) {
        if (
            !product ||
            !["lot", "serial"].includes(product.tracking) ||
            barcodeData?.lot ||
            barcodeData?.lotName
        ) {
            return;
        }
        this._scannedTrackedProductWithoutLot = product;
        if (quantity) {
            this._pendingLotQuantity = quantity;
        }
    },

    _deferThisTrackedScan(product, args = {}) {
        return Boolean(
            this._deferManualLot &&
                this._scannedTrackedProductWithoutLot &&
                product &&
                product.id === this._scannedTrackedProductWithoutLot.id &&
                !args.lot_id &&
                !args.lot_name
        );
    },

    async updateLine(line, args) {
        if (this._deferThisTrackedScan(line?.product_id, args)) {
            return;
        }
        return super.updateLine(...arguments);
    },

    async _createNewLine(params) {
        const product = params.fieldsParams?.product_id;
        if (this._deferThisTrackedScan(product, params.fieldsParams)) {
            return false;
        }
        return super._createNewLine(...arguments);
    },

    clearPendingLot() {
        this.pendingLotSelection = null;
        this._scannedTrackedProductWithoutLot = false;
        this.trigger("update");
    },

    async createPendingLot(name) {
        const pending = this.pendingLotSelection;
        if (!pending || !name) {
            return;
        }
        const [lotId] = await this.orm.create("stock.lot", [
            {
                name,
                product_id: pending.product.id,
            },
        ]);
        await this.confirmPendingLot({
            id: lotId,
            name,
            display_name: name,
        });
    },

    async confirmPendingLot(lot) {
        const pending = this.pendingLotSelection;
        if (!pending || !lot?.id) {
            return;
        }
        this.pendingLotSelection = null;
        this._scannedTrackedProductWithoutLot = false;
        const lotRecord = {
            id: lot.id,
            name: lot.name || lot.display_name,
            display_name: lot.display_name || lot.name,
            product_id: pending.product.id,
        };
        this.cache.setCache({"stock.lot": [lotRecord]});
        const quantity =
            pending.product.tracking === "serial" ? 1 : pending.quantity || 1;
        const fieldsParams = this._convertDataToFieldsParams({
            product: pending.product,
            lot: lotRecord,
            quantity,
        });
        const line = await this._createNewLine({fieldsParams});
        const selected =
            line ||
            this.currentState.lines.find(
                (existing) =>
                    existing.product_id.id === pending.product.id &&
                    existing.lot_id?.id === lotRecord.id
            );
        if (selected) {
            this._selectLine(selected);
            this.trigger("playSound", "success");
        }
        this.trigger("update");
    },
});
