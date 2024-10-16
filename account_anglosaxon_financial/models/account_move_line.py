from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        """When doing a financial supplier invoice we want to post the product
        lines directly to their COGS account"""
        res = super()._compute_account_id()
        input_lines = self._filter_purchase_stock_lines()
        for line in input_lines:
            accounts = line.with_company(
                line.company_id
            ).product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=line.move_id.fiscal_position_id
            )
            if accounts:
                line.account_id = accounts["expense"]
        return res

    def _filter_purchase_stock_lines(self):
        return self.filtered(
            lambda line: (
                line.with_context(ignore_financial=True)._eligible_for_cogs()
                and line.move_id.company_id.anglo_saxon_accounting
                and line.move_id.is_purchase_document()
            )
        )

    def _filter_financial_lines(self):
        """In the cases where we want to exclude financial lines
        filter them out"""
        invoice_lines = self
        if self._context.get("exclude_financial"):
            invoice_lines = invoice_lines.filtered(
                lambda s: not s.move_id.anglo_saxon_financial
            )
        return invoice_lines

    def _eligible_for_cogs(self):
        self.ensure_one()
        if (
            not self.env.context.get("ignore_financial")
            and self.move_id.anglo_saxon_financial
            or self.env.context.get("anglo_saxon_financial")
        ):
            return False
        return super()._eligible_for_cogs()
