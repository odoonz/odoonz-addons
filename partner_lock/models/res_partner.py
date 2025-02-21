# Copyright 2022 Graeme Gellatly, MoaHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_locked = fields.Boolean("Locked")

    def _unlocked_fields(self):
        "Inherit this function if you want to unlock other fields"
        return [
            "customer_rank",
            "supplier_rank",
            "child_ids",
            "risk_invoice_open",
            "risk_invoice_unpaid",
            "risk_account_amount",
            "risk_account_amount_unpaid",
            "risk_sale_order",
            "is_locked",
            "receipt_reminder_email",
            "reminder_date_before_receipt",
        ]

    def write(self, vals):
        self._check_locked_partners(vals)
        return super().write(vals)

    def _check_locked_partners(self, vals):
        if not self.env.user.has_groups("partner_lock.group_res_partner_unlock"):
            locked_records = self.env["res.partner"]
            for record in self.filtered(lambda s: s.is_locked):
                if not all([v in self._unlocked_fields() for v in vals]):
                    locked_records |= record
            if locked_records:
                _logger.debug("Partner Lock Fields: " + ", ".join(vals.keys()))
                raise ValidationError(locked_records._prepare_locked_record_error())

    def _prepare_locked_record_error(self):
        return "\n  - ".join(
            [
                _(
                    "Cannot update locked partner record. "
                    "The following records are locked"
                )
            ]
            + self.mapped("name")
        )
