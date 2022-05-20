# Copyright 2014 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: skip-file
# flake8: noqa
# we copy from odoo so easier to keep in line for modifications

from itertools import chain

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class ProductPricelist(models.Model):
    """
    Inherited class - to change pricing calculation and options
    """

    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(
        self,
        products_qty_partner,
        date,
        uom_id,
        prod_tmpl_ids,
        prod_ids,
        categ_ids,
    ):
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id', 'active'])
        products = self.env['product.product'].browse(prod_ids)
        price_categ_ids = list(set(products.tmpl_price_categ_ids.ids + products.price_categ_ids.ids))
        self.env.cr.execute(
            "SELECT item.id "
            "FROM product_pricelist_item AS item "
            "LEFT JOIN product_category AS categ "
            "ON item.categ_id = categ.id "
            "LEFT JOIN pricelist_item_product_rel AS pipr "
            "ON item.id = pipr.pricelist_item_id "
            "LEFT JOIN pricelist_item_tmpl_rel pitr "
            "ON item.id=pitr.pricelist_item_id "
            "WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s)) "
            "AND (pitr.tmpl_id IS NULL OR pitr.tmpl_id = any(%s)) "
            "AND (item.product_id IS NULL OR item.product_id = any(%s)) "
            "AND (pipr.prod_id IS NULL OR pipr.prod_id = any(%s)) "
            "AND (item.categ_id IS NULL OR item.categ_id = any(%s)) "
            "AND (item.price_categ_id IS NULL OR item.price_categ_id = any(%s)) "
            "AND (item.pricelist_id = %s) "
            "AND (item.date_start IS NULL OR item.date_start<=%s) "
            "AND (item.date_end IS NULL OR item.date_end>=%s) "
            "ORDER BY item.applied_on, item.min_quantity desc, categ.complete_name desc, item.name, item.id desc ",
            (
                prod_tmpl_ids,
                prod_tmpl_ids,
                prod_ids,
                prod_ids,
                categ_ids,
                price_categ_ids,
                self.id,
                date,
                date,
            ),
        )

        # Changes: due to chance of duplicates we need to filter this result
        # but retain order
        seen = set()
        item_ids = [x[0] for x in self._cr.fetchall() if (x not in seen or seen.add(x))]
        # End Changes
        items = self.env["product.pricelist.item"].browse(item_ids)
        return items

    def _is_applicable_for(self, product, qty_in_product_uom):
        res = super()._is_applicable_for(product, qty_in_product_uom)
        if res:
            return res
        res = True
        is_product_template = product._name == 'product.template'
        if is_product_template:
            #  Changes: We check the many2many version
            product_id = product.product_variant_id.id if self.product_variant_count == 1 else 0
            if self.product_tmpl_ids and (
                product.id not in self.product_tmpl_ids.ids
            ):
                res = False
            elif self.price_categ_id and (
                product.id not in self.price_categ_id.product_tmpl_ids.ids
                and product_id not in self.price_categ_id.product_ids.ids
            ):
                res = False
        else:
            if self.product_tmpl_ids and (
                product.product_tmpl_id.id not in self.product_tmpl_ids.ids
            ):
                res = False
            elif self.product_ids and (product.id not in self.product_ids.ids):
                res = False
        # Then we check the price category
            elif self.price_categ_id and (
                product.product_tmpl_id.id
                not in self.price_categ_id.product_tmpl_ids.ids
                and product.id not in self.price_categ_id.product_ids.ids
            ):
                res = False
        return res
