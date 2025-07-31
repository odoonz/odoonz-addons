from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "order_id.force_invoiced",
    )
    def _compute_risk_amount(self):
        forced = self.filtered(lambda line: line.order_id.force_invoiced)
        for line in forced:
            line.risk_amount = 0.0
        return super(SaleOrderLine, self - forced)._compute_risk_amount()
