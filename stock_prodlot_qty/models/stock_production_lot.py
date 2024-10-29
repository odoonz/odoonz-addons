# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockProductionLot(models.Model):

    _inherit = "stock.lot"

    @api.depends("name", "quant_ids", "quant_ids.quantity")
    @api.depends_context("show_qty")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for lot in self._show_with_quantities():
            lot.display_name = lot._display_name_show_qty()
        return res

    def _show_with_quantities(self):
        return self if self.env.context.get("show_qty") else self.env["stock.lot"]

    def _display_name_show_qty(self):
        self.ensure_one()
        return f"{self.display_name} ({int(self.product_qty)})"
