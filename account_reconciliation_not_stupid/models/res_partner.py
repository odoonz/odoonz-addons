from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def open_payment_matching_screen(self):
        # Open reconciliation view for customers/suppliers
        action_context = {
            "show_mode_selector": False,
            "company_ids": self.mapped("company_id").ids,
            "partner_ids": self.mapped("commercial_partner_id").ids,
            "mode": self.env.context.get("mode", "customers"),
        }
        return {
            "type": "ir.actions.client",
            "tag": "manual_reconciliation_view",
            "context": action_context,
        }
