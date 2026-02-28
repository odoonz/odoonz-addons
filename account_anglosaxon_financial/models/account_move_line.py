from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        """When doing a financial supplier invoice we want to post the product
        lines directly to their expense account instead of stock valuation"""
        res = super()._compute_account_id()
        input_lines = self._filter_purchase_financial_lines()
        for line in input_lines:
            accounts = line.with_company(
                line.company_id
            ).product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=line.move_id.fiscal_position_id
            )
            if accounts and accounts.get("expense"):
                line.account_id = accounts["expense"]
        return res

    def _filter_purchase_financial_lines(self):
        return self.filtered(
            lambda line: (
                line.with_context(ignore_financial=True)._eligible_for_stock_account()
                and line.move_id.anglo_saxon_financial
                and line.move_id.company_id.anglo_saxon_accounting
                and line.move_id.is_purchase_document()
            )
        )

    def _filter_financial_lines(self):
        """Exclude financial-only invoice lines when context requests it."""
        if self.env.context.get("exclude_financial"):
            return self.filtered(lambda s: not s.move_id.anglo_saxon_financial)
        return self

    def _eligible_for_stock_account(self):
        self.ensure_one()
        if (
            not self.env.context.get("ignore_financial")
            and self.move_id.anglo_saxon_financial
        ):
            return False
        return super()._eligible_for_stock_account()
