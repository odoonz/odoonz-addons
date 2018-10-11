# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


def _get_default_taxes(line, partner=None, inv_type="out_invoice"):
    InvoiceLine = line.env["account.invoice.line"]
    fpos = (
        line.order_id.fiscal_position_id
        or line.order_id.partner_id.property_account_position_id
    )
    account = InvoiceLine.get_invoice_line_account(
        inv_type, line.product_id, fpos, line.company_id
    )

    tax_field = (
        "taxes_id" if inv_type.startswith("out_") else "supplier_taxes_id"
    )

    company_tax_field = (
        "account_sale_tax_id" if inv_type.startswith("out_") else "account_purchase_tax_id"
    )

    # Don't try to collapse the filtering, needs independent evaluation of
    # each possibility.
    taxes = line.product_id[tax_field].filtered(
        lambda t: t.company_id == line.company_id
    ) or account.tax_ids.filtered(
        lambda t: t.company_id == line.company_id
        ) or line.company_id[company_tax_field]

    return fpos.map_tax(taxes, line.product_id, partner) if fpos else taxes


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            line.tax_id = _get_default_taxes(
                line, line.order_id.partner_shipping_id
            )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            line.taxes_id = _get_default_taxes(
                line, line.order_id.partner_id, "in_invoice"
            )


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange("account_id")
    def _onchange_account_id(self):
        super()._onchange_account_id()
        if not self.product_id and self.account_id:
            company_id = self.company_id or self.env.user.company_id
            self.invoice_line_tax_ids = self.invoice_line_tax_ids.filtered(
                lambda r: r.company_id == company_id
            )
