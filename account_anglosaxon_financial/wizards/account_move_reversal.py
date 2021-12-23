# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    anglo_saxon_refund_type = fields.Selection(
        [("financial", "Financial Only"), ("stock", "Stock Affected")],
        string="Impact of Refund",
        required=True,
        default="financial",
    )
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    def reverse_moves(self, mode="refund"):
        res = super().reverse_moves()
        if (
            self.refund_method == "modify"
            and self.anglo_saxon_refund_type == "financial"
        ):
            self.new_move_ids.toggle_financial()
        return res
