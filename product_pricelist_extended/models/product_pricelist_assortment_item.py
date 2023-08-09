# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductPricelistAssortmentItem(models.Model):

    _name = "product.pricelist.assortment.item"
    _description = "Product Pricelist Assortment Item"
    _inherit = "product.pricelist.item"

    assortment_filter_id = fields.Many2one(
        comodel_name="ir.filters",
        domain=[("is_assortment", "=", True)],
        string="Assortment",
        ondelete="restrict",
        required=True,
    )
    pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="assortment_item_id",
        help="Pricelist items created automatically",
    )
    applied_on = fields.Selection(compute="_compute_applied_on", store=True)

    @api.depends("assortment_filter_id", "assortment_filter_id.model_id")
    @api.onchange("assortment_filter_id")
    def _compute_applied_on(self):
        model_map = {
            "product.product": "0_product_variant",
            "product.template": "1_product",
            "product.category": "2_product_category",
        }
        for rec in self:
            rec.applied_on = model_map.get(rec.assortment_filter_id.model_id, "0_product_variant")

    def _get_pricelist_item_name_price(self):
        super()._get_pricelist_item_name_price()
        for rec in self:
            if rec.assortment_filter_id:
                rec.name = rec.assortment_filter_id.name

    def _get_pricelist_category_values(self, categs, default_values):
        list_values = []
        categs |= self.assortment_filter_id.whitelist_template_ids
        categs -= self.assortment_filter_id.blacklist_template_ids
        item_ids = set()
        for categ in categs:
            values = default_values.copy()
            values.update(
                {
                    "pricelist_id": self.pricelist_id.id,
                    "assortment_item_id": self.id,
                    "applied_on": "2_product_category",
                    "categ_id": categ.id,
                }
            )
            list_values.append(values)
            item_ids.add(categ.id)
        return list_values, item_ids

    def _get_pricelist_template_values(self, templates, default_values):
        list_values = []
        templates |= self.assortment_filter_id.whitelist_template_ids
        templates -= self.assortment_filter_id.blacklist_template_ids
        item_ids = set()
        for tmpl in templates:
            values = default_values.copy()
            values.update(
                {
                    "pricelist_id": self.pricelist_id.id,
                    "assortment_item_id": self.id,
                    "applied_on": "1_product",
                    "product_tmpl_id": tmpl.id,
                }
            )
            list_values.append(values)
            item_ids.add(tmpl.id)
        return list_values, item_ids

    def _get_pricelist_product_values(self, products, default_values):
        list_values = []
        item_ids = set()
        products |= self.assortment_filter_id.whitelist_product_ids
        products -= self.assortment_filter_id.blacklist_product_ids
        for product in products:
            values = default_values.copy()
            values.update(
                {
                    "pricelist_id": self.pricelist_id.id,
                    "assortment_item_id": self.id,
                    "applied_on": "0_product_variant",
                    "product_id": product.id,
                }
            )
            item_ids.add(product.id)
            list_values.append(values)
        return list_values, item_ids

    def _get_pricelist_item_values(self):
        """
        Get a list of values to create new product.pricelist.item
        :return: list of dict
        """
        self.ensure_one()
        items = self._get_product_from_assortment()
        list_values = []
        # fields to ignore to create pricelist item
        blacklist = models.MAGIC_COLUMNS + [self.CONCURRENCY_CHECK_FIELD]
        blacklist.extend(["assortment_filter_id", "pricelist_item_ids"])
        default_values = {
            k: self._fields.get(k).convert_to_write(self[k], self)
            for k in self._fields.keys()
            if k not in blacklist
        }
        return getattr(self, f"_get_pricelist_{self.assortment_filter_id.model_id.split('.')[1]}_values")(items, default_values)

    def _get_product_from_assortment(self):
        domain = self.assortment_filter_id._get_eval_domain()
        products = self.env[self.assortment_filter_id.model_id].search(domain)
        return products

    def _get_related_items(self, new_item_ids=False):
        domain = [('assortment_item_id', 'in', self.ids)]
        if isinstance(new_item_ids, set):
            new_item_ids = list(new_item_ids)
        if new_item_ids:
            if self.applied_on == '0_product_variant':
                domain.append(('product_id', 'not in', new_item_ids))
            elif self.applied_on == '1_product':
                domain.append(('product_tmpl_id', 'not in', new_item_ids))
            elif self.applied_on == '2_product_category':
                domain.append(('categ_id', 'not in', new_item_ids))
        return self.env['product.pricelist.item'].search(domain)

    def _update_assortment_items(self):
        """
        Update the pricelist with current assortment:
        - Prepare values for new assorment items;
        - Delete no longer included items.
        - Create new assortments items;

        :return: bool
        """
        self.ensure_one()
        if not self.assortment_filter_id.active:
            _logger.info(
                "The assortment item %s is ignored because the "
                "related assortment/filter is not active",
                self.display_name,
            )
            return False
        item_field = {'0_product_variant': 'product_id', '1_product': 'product_tmpl_id', '2_product_category': 'categ_id'}[self.applied_on]
        item_obj = self.env["product.pricelist.item"]
        items_values, item_ids = self._get_pricelist_item_values()
        # These items are no longer valid so we remove them
        self._get_related_items(item_ids).unlink()
        for item_value in items_values:
            item_obj.create(item_value)
        return True

    @api.constrains('product_id', 'product_tmpl_id', 'categ_id')
    def _check_product_consistency(self):
        for rec in self:
            if any((rec.product_id, rec.product_tmpl_id, rec.categ_id)):
                raise ValidationError(_("You can't set a product, a product template or a category on an assortment item."))
