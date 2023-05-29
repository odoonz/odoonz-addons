# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    bom_list_price = fields.Float(
        "List Price From BoM",
        compute="_compute_bom_list",
        digits="Product Price",
        compute_sudo=True,
    )

    @api.depends("list_price", "price_extra", "lst_price_from_bom")
    @api.depends_context("uom")
    def _compute_product_lst_price(self):
        to_uom = None
        if "uom" in self._context:
            to_uom = self.env["uom.uom"].browse(self._context["uom"])
        bom_products = self.filtered(lambda s: s.lst_price_from_bom)
        res = super(ProductProduct, self - bom_products)._compute_product_lst_price()
        for product in bom_products:
            if to_uom:
                list_price = product.uom_id._compute_price(
                    product.bom_list_price, to_uom
                )
            else:
                list_price = product.bom_list_price
            product.lst_price = list_price
        return res

    def _compute_bom_list_price(self, bom):
        return self._compute_bom_price_by_type(
            bom, price="lst_price", labour="price_hour"
        )

    def _compute_bom_list(self):
        return self.action_bom_list()

    def button_bom_list(self):
        self.ensure_one()
        self._set_list_price_from_bom()

    def action_bom_list(self):
        boms_to_recompute = self.env["mrp.bom"].search(
            [
                "|",
                ("product_id", "in", self.ids),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "in", self.mapped("product_tmpl_id").ids),
            ]
        )
        for product in self:
            product._set_list_price_from_bom(boms_to_recompute)

    def _set_list_price_from_bom(self, boms_to_recompute=False):
        self.ensure_one()
        bom = self.env["mrp.bom"]._bom_find(product=self)
        if bom:
            self.bom_list_price = self._compute_bom_list_price(bom)
        else:
            self.bom_list_price = 0.0

    def price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        bom_prices = {}
        if price_type == "list_price":
            lst_price_from_bom = self.filtered(lambda s: s.lst_price_from_bom)
            self = self - lst_price_from_bom
            bom_prices = {
                product.id: product.bom_list_price for product in lst_price_from_bom
            }
        prices = super().price_compute(
            price_type, uom=uom, currency=currency, company=company, date=date
        )
        prices.update(bom_prices)
        return prices
