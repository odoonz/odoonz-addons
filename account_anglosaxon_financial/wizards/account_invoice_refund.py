# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.onchange("filter_refund")
    def compute_anglo_saxon_state(self):
        if self.env.context.get("active_ids"):
            inv = self.env["account.invoice"].browse(self.env.context["active_ids"])
            anglo_saxon = inv.company_id.anglo_saxon_accounting
        else:
            anglo_saxon = self.env.user.company_id.anglo_saxon_accounting
        for record in self:
            record.anglo_saxon_accounting = anglo_saxon

    anglo_saxon_refund_type = fields.Selection(
        [("financial", "Financial Only"), ("stock", "Stock Affected")],
        string="Impact of Refund",
        required=True,
        default="financial",
    )
    anglo_saxon_accounting = fields.Boolean()

    @api.multi
    def compute_refund(self, mode="refund"):
        res = super().compute_refund(mode=mode)
        if (
            mode == "refund"
            and self.anglo_saxon_refund_type == "financial"
            and isinstance(res, dict)
            and res.get("domain")
        ):
            for left, op, right in res["domain"]:
                if left == "id" and op == "in":
                    for inv in self.env["account.invoice"].browse(right):
                        if inv and not inv.anglo_saxon_financial:
                            inv.toggle_financial()
        return res
