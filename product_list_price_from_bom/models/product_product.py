# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    bom_list_price = fields.Float(
        "List Price From BoM", compute="_compute_bom_list", digits="Product Price"
    )

    @api.depends("list_price", "price_extra", "lst_price_from_bom")
    @api.depends_context("uom")
    def _compute_product_lst_price(self):
        to_uom = None
        if "uom" in self._context:
            to_uom = self.env["uom.uom"].browse(self._context["uom"])
        bom_products = self.filtered(lambda s: s.lst_price_from_bom)
        for product in bom_products:
            if to_uom:
                list_price = product.uom_id._compute_price(
                    product.bom_list_price, to_uom
                )
            else:
                list_price = product.bom_list_price
            product.lst_price = list_price
        return super(ProductProduct, self - bom_products)._compute_product_lst_price()

    def _compute_bom_list_price(self, bom, boms_to_recompute=False):
        self.ensure_one()
        if not bom:
            return 0

        if not boms_to_recompute:
            boms_to_recompute = []
        _dummy, bom_lines = bom.explode(self, 1)
        total = 0
        for line, explode_details in bom_lines:
            total += (
                line.product_id.uom_id._compute_price(
                    line.product_id.lst_price, line.product_uom_id
                )
                * explode_details["qty"]
            )
        # for opt in bom.operation_ids:
        #     duration_expected = (
        #         opt.workcenter_id.time_start +
        #         opt.workcenter_id.time_stop +
        #         opt.time_cycle)
        #     total += (duration_expected / 60) * opt.workcenter_id.costs_hour # Labour margin
        # for line in bom.bom_line_ids:
        #     if line._skip_bom_line(self):
        #         continue

        #     # Compute recursive if line has `child_line_ids`
        #     if line.child_bom_id and line.child_bom_id in boms_to_recompute:
        #         child_total = line.product_id._compute_bom_list_price(line.child_bom_id, boms_to_recompute=boms_to_recompute)
        #         total += line.product_id.uom_id._compute_price(child_total, line.product_uom_id) * line.product_qty
        #     else:
        #         total += line.product_id.uom_id._compute_price(line.product_id.lst_price, line.product_uom_id) * line.product_qty
        return bom.product_uom_id._compute_price(total / bom.product_qty, self.uom_id)

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
            self.bom_list_price = self._compute_bom_list_price(
                bom, boms_to_recompute=boms_to_recompute
            )

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        bom_prices = {}
        if price_type == "list_price":
            lst_price_from_bom = self.filtered(lambda s: s.lst_price_from_bom)
            self = self - lst_price_from_bom
            bom_prices = {
                product.id: product.bom_list_price for product in lst_price_from_bom
            }
        prices = super().price_compute(
            price_type, uom=uom, currency=currency, company=company
        )
        prices.update(bom_prices)
        return prices
