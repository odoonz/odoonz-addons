# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.http import request

from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController


class StockBarcodeController(StockBarcodeController):
    def _try_open_picking(self, barcode):
        """Open the later transfer when the scanned number is a finished prior one."""
        picking_model = request.env["stock.picking"]
        named = picking_model.search([("name", "=", barcode)], limit=1)
        if not named or named.state in ("done", "cancel"):
            successors = picking_model._barcode_find_by_prior_transfer(barcode)
            if len(successors) == 1:
                return {"action": successors.action_open_picking_client_action()}
            if successors:
                return {"action": picking_model._barcode_action_for_pickings(successors)}
        return super()._try_open_picking(barcode)
