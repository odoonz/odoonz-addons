# Copyright 2022 Graeme Gellatly, O4SB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_locked = fields.Boolean("Locked")

    def unlocked_fields(self):
        return [
            "customer_rank",
            "supplier_rank",
            "child_ids",
            "risk_invoice_open",
            "risk_invoice_unpaid",
            "risk_account_amount",
            "risk_account_amount_unpaid",
            "risk_sale_order",
        ]

    def write(self, vals):
        locked_records = self.env["res.partner"]
        for record in self.filtered(lambda s: s.is_locked):
            if not all([v in self.unlocked_fields() for v in vals]):
                locked_records |= record
        if locked_records:
            raise ValidationError(
                "\n  - ".join(
                    [
                        _(
                            "Cannot update locked partner record. "
                            "The following records are locked"
                        )
                    ]
                    + locked_records.mapped("name")
                )
            )
        return super().write(vals)
