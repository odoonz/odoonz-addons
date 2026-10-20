import {Component} from "@odoo/owl";
import {Many2XAutocomplete} from "@web/views/fields/relational_utils";
import {_t} from "@web/core/l10n/translation";

export class CountLotPicker extends Component {
    static template = "stock_barcode_lot_prompt.CountLotPicker";
    static components = {Many2XAutocomplete};
    static props = {};

    setup() {
        this.activeActions = {};
        this.specification = {name: {}};
    }

    get product() {
        return this.env.model.pendingLotSelection.product;
    }

    get lotLabel() {
        return _t("Serial/Lot Number");
    }

    getDomain() {
        return [["product_id", "=", this.product.id]];
    }

    quickCreate(name) {
        return this.env.model.createPendingLot(name);
    }

    onLotSelected(records) {
        const lot = records && records[0];
        if (!lot) {
            return;
        }
        return this.env.model.confirmPendingLot(lot);
    }

    cancel(ev) {
        ev.stopPropagation();
        this.env.model.clearPendingLot();
    }
}
