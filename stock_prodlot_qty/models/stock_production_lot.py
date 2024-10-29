# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockProductionLot(models.Model):

    _inherit = "stock.lot"

    @api.model
    def _show_quantities(self):
        return self.env.context.get("show_qty")

    def _display_name_show_qty(self):
        self.ensure_one()
        return f"{self.display_name} ({int(self.product_qty)})"

    @api.depends('name', 'quant_ids', 'quant_ids.quantity')
    @api.depends_context('show_qty')
    def _compute_display_name(self):
        res = super()._compute_display_name
        if self._show_quantities():
            for lot in self:
                lot.display_name = lot._display_name_show_qty
        return res
