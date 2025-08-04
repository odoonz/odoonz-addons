from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    order_partner_id = fields.Many2one(
        "res.partner",
        string="Order Partner",
    )
    invoice_partner_id = fields.Many2one(
        "res.partner",
        string="Invoice Partner",
    )
    orig_commercial_partner_id = fields.Many2one(
        "res.partner",
        string="Original Commercial Partner",
    )

    def _select(self) -> SQL:
        return SQL(
            """%s,
            move.order_partner_id,
            move.order_invoice_id invoice_partner_id,
            COALESCE(op.commercial_partner_id, move.commercial_partner_id)
              as orig_commercial_partner_id
            """,
            super()._select(),
        )

    def _from(self) -> SQL:
        return SQL(
            "%s LEFT JOIN res_partner op ON op.id = move.order_partner_id",
            super()._from(),
        )
