# Copyright 2022 Graeme Gellatly, MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerSetRiskWizard(models.TransientModel):
    _description = "Set Credit Limits"
    _name = "partner.set.risk.wizard"

    risk_invoice_unpaid_limit = fields.Float(string="Overdue Invoices Limit")
    credit_limit = fields.Float(string="Overall Credit Limit")
    credit_policy = fields.Char()

    def set_limits(self):
        self.ensure_one()
        partners = self.env["res.partner"].browse(self.env.context.get("active_ids"))
        partners = partners.filtered(lambda s: not s.parent_id)
        partners.write(
            {
                "credit_limit": self.credit_limit,
                "credit_policy": self.credit_policy,
                "risk_invoice_unpaid_limit": self.risk_invoice_unpaid_limit,
                "risk_sale_order_include": True,
                "risk_invoice_draft_include": True,
                "risk_invoice_open_include": True,
                "risk_invoice_unpaid_include": True,
                "risk_account_amount_include": True,
                "risk_account_amount_unpaid_include": True,
            }
        )
        return {"type": "ir.actions.act_window_close"}
