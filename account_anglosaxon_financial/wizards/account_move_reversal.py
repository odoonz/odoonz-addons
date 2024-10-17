# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    anglo_saxon_refund_type = fields.Selection(
        [
            ("financial", "Financial Only"),
            ("stock", "Stock Affected"),
            ("service", "No Stock on Invoice"),
        ],
        default="financial",
        string="Impact of Refund",
        help="If you are just correcting a pricing error then select Financial"
        ", otherwise if stock was returned, use Stock",
    )
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    def _prepare_default_reversal(self, move):
        default_values = super()._prepare_default_reversal(move)
        if self._is_price_credit(move):
            default_values["anglo_saxon_financial"] = True
        return default_values

    def reverse_moves(self, is_modify=False):
        """We need to access is_modify in the preparing defaults functions
        and have no direct access"""
        self = self.with_context(is_price_credit=not is_modify)
        return super().reverse_moves(is_modify=is_modify)

    def _is_price_credit(self, move):
        return (
            self.anglo_saxon_refund_type == "financial"
            and self.env.context.get("is_price_credit")
            and move.move_type != "entry"
        )
