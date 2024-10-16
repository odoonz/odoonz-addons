from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("invoice_lines.move_id.anglo_saxon_financial")
    def _compute_qty_invoiced(self):
        """Override here to exclude quantities on price credits"""
        self = self.with_context(exclude_financial=True)
        return super()._compute_qty_invoiced()

    def _get_invoice_lines(self):
        return super()._get_invoice_lines()._filter_financial_lines()
