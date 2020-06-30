# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


def _get_default_taxes(line, partner=None, inv_type="out_invoice"):
    company = line.company_id or line.order_id.company_id
    fpos = (
        line.order_id.fiscal_position_id
        or line.order_id.partner_id.property_account_position_id
    )
    company_tax_field = (
        "account_sale_tax_id"
        if inv_type.startswith("out_")
        else "account_purchase_tax_id"
    )
    tax_field = "taxes_id" if inv_type.startswith("out_") else "supplier_taxes_id"
    account_type = "income" if inv_type.startswith("out_") else "expense"
    tax_ids = line.env["account.tax"]
    if line.product_id[tax_field].filtered(lambda tax: tax.company_id == company):
        tax_ids = line.product_id[tax_field].filtered(
            lambda tax: tax.company_id == company
        )
    elif line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
        account_type
    ].tax_ids:
        tax_ids = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
            account_type
        ].tax_ids
    if not tax_ids:
        tax_ids = company[company_tax_field]
    return fpos.map_tax(tax_ids, line.product_id, partner) if fpos else tax_ids


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            if not line.tax_id:
                line.tax_id = _get_default_taxes(
                    line, line.order_id.partner_shipping_id
                )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # @api.onchange("product_id")
    # def onchange_product_id(self):
    #     result = super().onchange_product_id()
    #     self._compute_tax_id()
    #     return result

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            if not line.taxes_id:
                line.taxes_id = _get_default_taxes(
                    line, line.order_id.partner_id, "in_invoice"
                )


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        partner = values["supplier"].name
        pol = self.env["purchase.order.line"].new(
            {
                "order_id": po.id,
                "product_id": po.product_id,
                "company_id": po.company_id,
            }
        )
        res.update(
            taxes_id=[
                (6, 0, _get_default_taxes(pol, partner, inv_type="in_invoice").ids)
            ]
        )
        return res
