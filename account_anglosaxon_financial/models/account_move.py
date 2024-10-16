# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    anglo_saxon_financial = fields.Boolean("Financial Only", default=False)
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        """
        When we add a purchase order to a manually created invoice
        we know we want anglosaxon, unless we are recharging on
        behalf of another company
        """
        purchase = self.purchase_id or self.purchase_vendor_bill_id.purchase_order_id
        if purchase and purchase.company_id == self.company_id:
            self.anglo_saxon_financial = False
        return super()._onchange_purchase_auto_complete()

    def toggle_financial(self):
        for move in self.filtered(lambda s: s.state == "draft"):
            move.anglo_saxon_financial = not move.anglo_saxon_financial
            move.filtered(
                lambda s: s.move_type in ("in_invoice", "in_refund")
            )._set_in_line_cogs_accounts()

    def _set_in_line_cogs_accounts(self):
        """When doing a financial supplier invoice we want to post the product
        lines directly to their COGS account"""
        for line in self.invoice_line_ids:
            if line.product_id:
                line._compute_account_id()

    def _stock_account_prepare_anglo_saxon_in_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_in_lines_vals()

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_out_lines_vals()

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_anglo_saxon_reconcile_valuation(product=product)
