# -*- coding: utf-8 -*-
# Copyright 2014 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: skip-file
# flake8: noqa
# we copy from odoo so easier to keep in line for modifications

from itertools import chain

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError

# noinspection PyUnresolvedReferences
import odoo.addons.decimal_precision as dp


class ProductPricelist(models.Model):
    """
    Inherited class - to change pricing calculation and options
    """
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False,
                            uom_id=False):
        """

        :param products_qty_partner: list of tuples
        :param date: string
        :param uom_id: unit of measure integer
        :return: dictionary of format key=integer product.id, value=float price
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        is_product = products[0]._name == "product.product"

        categ_ids = {}
        # Changes: We search for price categories as well
        price_categ_ids = []
        for p in products:
            categ = p.categ_id
            if is_product:
                price_categ_ids.extend([c.id for c in p.price_categ_ids])
            price_categ_ids.extend([c.id for c in p.tmpl_price_categ_ids])
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids.keys())
        price_categ_ids = list(set(price_categ_ids))
        # End Changes

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        # Changes: Add search of multiple products and templates
        # plus price category to SQL
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'LEFT JOIN pricelist_item_product_rel AS pipr '
            'ON item.id = pipr.pricelist_item_id '
            'LEFT JOIN pricelist_item_tmpl_rel pitr '
            'ON item.id=pitr.pricelist_item_id ' 
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s)) '
            'AND (pitr.tmpl_id IS NULL OR pitr.tmpl_id = any(%s)) '
            'AND (item.product_id IS NULL OR item.product_id = any(%s)) '
            'AND (pipr.prod_id IS NULL OR pipr.prod_id = any(%s)) '
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.price_categ_id IS NULL OR item.price_categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s) '
            'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
            (prod_tmpl_ids, prod_tmpl_ids, prod_ids, prod_ids,
             categ_ids, price_categ_ids, self.id, date, date))

        # Changes: due to chance of duplicates we need to filter this result
        # but retain order
        seen = set()
        item_ids = [x[0] for x in self._cr.fetchall()
                    if (x not in seen or seen.add(x))]
        # End Changes
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                    #  Changes: We check the many2many version
                    if rule.product_tmpl_ids and (product.id not in rule.product_tmpl_ids.ids):
                        continue
                    if rule.product_ids and product.product_variant_count == 1 and (
                                product.product_variant_id.id not in rule.product_ids.ids):
                        continue
                    # Then we check the price category
                    if rule.price_categ_id and product.product_variant_count == 1 and (
                                    product.id not in rule.price_categ_id.product_tmpl_ids.ids and
                                    product.product_variant_id.id not in rule.price_categ_id.product_ids.ids):
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue
                    #  Changes: We check the many2many version
                    if rule.product_tmpl_ids and (product.product_tmpl_id.id not in
                                rule.product_tmpl_ids.ids):
                        continue
                    if rule.product_ids and (product.id not in rule.product_ids.ids):
                        continue
                    # Then we check the price category
                    if rule.price_categ_id and (
                                    product.product_tmpl_id.id not in rule.price_categ_id.product_tmpl_ids.ids and
                                    product.id not in rule.price_categ_id.product_ids.ids):
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                # Changes - add in code inclusion and exclusion rules
                if rule.code_inclusion and rule.code_inclusion not in (
                            product.default_code or ''):
                    continue
                if rule.code_exclusion and rule.code_exclusion in (
                            product.default_code or ''):
                    continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100.0))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100.0))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(price, self.currency_id, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results
