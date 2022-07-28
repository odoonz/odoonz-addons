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
        string="Impact of Refund",
    )
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    def reverse_moves(self):
        is_fin = (
            self.move_type != "entry" and self.anglo_saxon_refund_type == "financial"
        )
        if is_fin and self.refund_method == "refund":
            self = self.with_context(no_move_lines=True)
        res = super().reverse_moves()
        if is_fin:
            self.new_move_ids.toggle_financial()
        return res
