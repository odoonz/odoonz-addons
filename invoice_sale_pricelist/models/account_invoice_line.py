# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceLine(models.Model):

    _inherit = "account.move.line"

    def _get_sale_price_unit(self):
        product_ctx = dict(
            quantity=self.quantity,
            date=self.move_id.invoice_date,
            uom=self.product_uom_id.id,
            partner_id=self.move_id.partner_id.commercial_partner_id.id,
        )

        if "pricelist" not in product_ctx:
            pricelist = self.sale_line_ids.mapped("order_id.pricelist_id")

            if len(pricelist) != 1:
                pricelist = self.move_id.partner_id.property_product_pricelist
            product_ctx.update({"pricelist": pricelist.id})

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        taxes = (
            self.product_id.taxes_id.filtered(lambda r: r.company_id == company_id)
            or self.account_id.tax_ids
        )

        product = (
            self.env["product.product"]
            .with_context(**product_ctx)
            .browse(self.product_id.id)
        )

        return self.env["account.tax"]._fix_tax_included_price(
            product.price, taxes, self.tax_ids
        )

    def _get_computed_price_unit(self):
        if self.move_id.is_sale_document(include_receipts=True):
            return self._get_sale_price_unit()
        else:
            return super()._get_computed_price_unit()
