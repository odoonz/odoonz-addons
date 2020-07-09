from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def open_payment_matching_screen(self):
        # Open reconciliation view for customers/suppliers
        action_context = {
            "company_ids": [self.env.user.company_id.id],
            "partner_ids": self.mapped("commercial_partner_id").ids,
            "mode": self.env.context.get("mode", "customers"),
        }
        return {
            "type": "ir.actions.client",
            "tag": "manual_reconciliation_view",
            "context": action_context,
        }

    customer = fields.Boolean(
        string="Is a Customer", help="Check this box if this contact is a customer."
    )
    supplier = fields.Boolean(
        string="Is a Vendor", help="Check this box if this contact is a vendor."
    )
