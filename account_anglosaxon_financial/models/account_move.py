# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    anglo_saxon_financial = fields.Boolean("Financial Only", default=False)
    anglo_saxon_accounting = fields.Boolean("company_id.anglo_saxon_accounting")

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
            if move.move_type in ("in_invoice", "in_refund"):
                for line in move.invoice_line_ids:
                    if line.product_id:
                        line.account_id = line._get_computed_account()

    def _stock_account_prepare_anglo_saxon_in_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_in_lines_vals()

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_out_lines_vals()

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_anglo_saxon_reconcile_valuation(product=product)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_account(self):
        self.ensure_one()
        if (
            self.product_id.type == "product"
            and (
                self.move_id.anglo_saxon_financial
                or self.env.context.get("anglo_saxon_financial")
            )
            and self.move_id.company_id.anglo_saxon_accounting
            and self.move_id.is_purchase_document()
        ):
            accounts = self.product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=self.move_id.fiscal_position_id
            )
            if accounts:
                return accounts["expense"]
        return super()._get_computed_account()
