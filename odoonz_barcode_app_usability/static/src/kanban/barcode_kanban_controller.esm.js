import {markup} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {StockBarcodeKanbanController} from "@stock_barcode/kanban/stock_barcode_kanban_controller";

patch(StockBarcodeKanbanController.prototype, {
    /**
     * Open a transfer returned for a prior-transfer scan.
     *
     * The core handler only follows an action that carries help text, which
     * is the operations list. A scan of the previous transfer opens that
     * transfer directly, so an action without help still has to run.
     */
    async _onBarcodeScannedHandler(barcode) {
        const kwargs = {barcode, context: this.props.context};
        const res = await this.model.orm.call(this.props.resModel, "filter_on_barcode", [], kwargs);
        const action = res.action;
        if (action) {
            if (action.help) {
                action.help = markup(action.help);
            }
            return this.actionService.doAction(action);
        }
        if (res.warning) {
            const params = {title: res.warning.title, type: "danger"};
            this.model.notification.add(res.warning.message, params);
        }
    },
});
