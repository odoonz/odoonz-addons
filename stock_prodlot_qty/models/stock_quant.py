from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.depends("quantity")
    @api.depends_context("show_qty")
    def _compute_display_name(self):
        """name that will be displayed in the detailed operation"""
        res = super()._compute_display_name()
        for quant in self._show_with_quantities():
            quant.display_name = quant._display_name_show_qty()
        return res

    def _show_with_quantities(self):
        return (
            self.filtered(lambda s: s.lot_id)
            if self.env.context.get("show_qty")
            else self.env["stock.quant"]
        )

    def _display_name_show_qty(self):
        self.ensure_one()
        return f"{self.display_name} ({int(self.quantity)})"
