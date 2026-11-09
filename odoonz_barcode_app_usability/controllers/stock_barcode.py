# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.http import request

from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController


class StockBarcodeController(StockBarcodeController):
    def _try_open_picking(self, barcode):
        """Open a transfer by name, ignoring case, or the open transfer that follows it.

        USB keyboard-wedge scanners flip letter case when Caps Lock is on, so
        a pick label such as ``HAN/OUT/00001`` can arrive as ``han/out/00001``.
        """
        picking_model = request.env["stock.picking"]
        named = picking_model.search([("name", "=ilike", barcode)], limit=1)
        if named and named.state not in ("done", "cancel"):
            return {"action": named.action_open_picking_client_action()}
        successors = picking_model._barcode_find_by_prior_transfer(barcode)
        if len(successors) == 1:
            return {"action": successors.action_open_picking_client_action()}
        if successors:
            return {"action": picking_model._barcode_action_for_pickings(successors)}
        return super()._try_open_picking(barcode)
