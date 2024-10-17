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

    def reverse_moves(self):
        is_fin = (
            self.move_type != "entry"
            and self.anglo_saxon_refund_type == "financial"
            and self.refund_method == "modify"
        )
