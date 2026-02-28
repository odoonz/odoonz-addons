# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class TaxFromAccount(models.AbstractModel):
    _name = "tax.from.account"
    _description = "Tax From Account Mixin"

    def _get_default_taxes(self, inv_type="out_invoice"):
        self.ensure_one()
        company = self.company_id or self.order_id.company_id
        fpos = self._get_fiscal_position()
        company_tax_field, tax_field, account = self._get_tax_fields_for_inv_type(
            inv_type
        )
        # Don't try to collapse the filtering, needs independent evaluation of
        # each possibility.
        taxes = (
            self.product_id[tax_field]._filter_taxes_by_company(company)
            or account.tax_ids._filter_taxes_by_company(company)
            or company[company_tax_field]
        )
        return fpos.map_tax(taxes) if fpos else taxes

    def _get_fiscal_position(self):
        return (
            self.order_id.fiscal_position_id
            or self.order_id.partner_id.property_account_position_id
        )

    def _get_tax_fields_for_inv_type(self, inv_type):
        fpos = self._get_fiscal_position()
        company_tax_field = (
            "account_sale_tax_id"
            if inv_type.startswith("out_")
            else "account_purchase_tax_id"
        )
        if inv_type.startswith("out_"):
            tax_field, account_type = "taxes_id", "income"
        else:
            tax_field, account_type = "supplier_taxes_id", "expense"
        account = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
            account_type
        ]
        return company_tax_field, tax_field, account


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "tax.from.account"]

    def _create_delivery_line(self, carrier, price_unit):
        sol = super()._create_delivery_line(carrier, price_unit)
        sol._compute_tax_id()
        return sol


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "tax.from.account"]

    def _compute_tax_ids(self):
        res = super()._compute_tax_ids()
        for line in self:
            if not line.tax_ids:
                line.tax_ids = line._get_default_taxes()
        return res


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "tax.from.account"]

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        for line in self:
            if not line.tax_ids:
                line.tax_ids = line._get_default_taxes("in_invoice")
        return res


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "tax.from.account"]

    def _get_computed_taxes(self):
        """
        Override to use default company taxes if not taxes found.
        """
        tax_ids = super()._get_computed_taxes()
        if tax_ids:
            return tax_ids
        if self.move_id.is_sale_document(include_receipts=True):
            tax_ids = self.move_id.company_id.account_sale_tax_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            tax_ids = self.move_id.company_id.account_purchase_tax_id
        return tax_ids
