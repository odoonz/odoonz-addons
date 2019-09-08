# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    anglo_saxon_financial = fields.Boolean("Financial Only")
    anglo_saxon_accounting = fields.Boolean("company_id.anglo_saxon_accounting")

    @api.onchange("purchase_id")
    def change_vendor_bill_purchase_id_anglo_saxon(self):
        """
        When we add a purchase order to a manually created invoice
        we know we want anglosaxon, unless we are recharging on
        behalf of another company
        """
        if not self.purchase_id:
            return {}
        if self.purchase_id.company_id == self.company_id:
            self.anglo_saxon_financial = False

    def toggle_financial(self):
        for record in self.filtered(lambda s: s.state == "draft"):
            record.anglo_saxon_financial = not record.anglo_saxon_financial
            if record.type in ("in_invoice", "in_refund"):
                for line in record.invoice_line_ids:
                    if line.product_id:
                        line.account_id = (
                            line.get_invoice_line_account(
                                record.type,
                                line.product_id,
                                record.fiscal_position_id,
                                record.company_id,
                            )
                            or line.account_id
                        )

    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        if i_line.invoice_id.anglo_saxon_financial:
            return []
        return super()._anglo_saxon_purchase_move_lines(i_line, res)

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line):
        if i_line.invoice_id.anglo_saxon_financial:
            return []
        return super()._anglo_saxon_sale_move_lines(i_line)

    def _anglo_saxon_reconcile_valuation(self, product=False):
        new_self = self.filtered(lambda s: not s.anglo_saxon_financial)
        if new_self:
            super(AccountInvoice, new_self)._anglo_saxon_reconcile_valuation(
                product=product
            )


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        """
        We override stock_account function to return the expense account
        for inwards invoices and refunds.
        Note: Context is checked as this method could arguably be called from
        an empty recordset (although it never is in core)
        :param type:
        :param product:
        :param fpos:
        :param company:
        :return: an account
        """
        try:
            if (
                company.anglo_saxon_accounting
                and (
                    self.invoice_id.anglo_saxon_financial
                    or self.env.context.get("anglo_saxon_financial")
                )
                and type in ("in_invoice", "in_refund")
                and product
                and product.type == "product"
            ):
                return product.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
                    "expense"
                ]
        except AttributeError:
            pass
        return super().get_invoice_line_account(type, product, fpos, company)
