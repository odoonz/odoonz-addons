# -*- coding: utf-8 -*-
# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        super(AccountInvoiceLine, self)._set_taxes()
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            return
        self.price_unit = self._get_sale_price_unit()

    def _get_sale_price_unit(self):
        product_ctx = dict(
            quantity=self.quantity,
            date=self.invoice_id.date_invoice,
            uom=self.uom_id.id)
        product_ctx.update(dict(self.env.context))

        if 'pricelist' not in product_ctx:
            pricelist = self.sale_line_ids.mapped('order_id.pricelist_id')

            if len(pricelist) != 1:
                pricelist = (
                    self.invoice_id.partner_id.property_product_pricelist)
            product_ctx.update({'pricelist': pricelist.id})

        taxes = self.product_id.taxes_id or self.account_id.tax_ids

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)

        product = self.product_id.with_context(**product_ctx)

        return self.env['account.tax']._fix_tax_included_price(
            product.price, taxes, self.invoice_line_tax_ids)
