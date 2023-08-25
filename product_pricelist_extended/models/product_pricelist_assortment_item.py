# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

BLACKLIST_FIELDS = [
    "blacklist_product_ids",
    "blacklist_template_ids",
    "blacklist_category_ids",
    "whitelist_product_ids",
    "whitelist_template_ids",
    "whitelist_category_ids",
]


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
    # NOTE: If extending with other models, make sure your whitelist/blacklist
    # fields are named in the same way, last word of the model in whitelist_<last>_ids
    # and blacklist_<last>_ids. These are applied in addition to the filter exclusions
    # for fine-grained control
    blacklist_product_ids = fields.Many2many(
        comodel_name="product.product", relation="assortment_item_product_blacklisted"
    )
    whitelist_product_ids = fields.Many2many(
        comodel_name="product.product", relation="assortment_item_product_whitelisted"
    )
    blacklist_template_ids = fields.Many2many(
        comodel_name="product.template", relation="assortment_item_tmpl_blacklisted"
    )
    whitelist_template_ids = fields.Many2many(
        comodel_name="product.template", relation="assortment_item_tmpl_whitelisted"
    )
    blacklist_category_ids = fields.Many2many(
        comodel_name="product.category", relation="assortment_item_categ_blacklisted"
    )
    whitelist_category_ids = fields.Many2many(
        comodel_name="product.category", relation="assortment_item_categ_whitelisted"
    )

    @api.depends("assortment_filter_id", "assortment_filter_id.model_id")
    @api.onchange("assortment_filter_id")
    def _compute_applied_on(self):
        model_map = {
            "product.product": "0_product_variant",
            "product.template": "1_product",
            "product.category": "2_product_category",
        }
        for rec in self:
            model = rec.assortment_filter_id.model_id
            rec.applied_on = model_map.get(model, "0_product_variant")
            if model == "product.product":
                rec.whitelist_template_ids = False
                rec.blacklist_template_ids = False
                rec.whitelist_category_ids = False
                rec.blacklist_category_ids = False
            elif model == "product.template":
                rec.whitelist_template_ids = rec.whitelist_product_ids.product_tmpl_id
                rec.blacklist_template_ids = rec.blacklist_product_ids.product_tmpl_id
                rec.whitelist_product_ids = False
                rec.blacklist_product_ids = False
                rec.whitelist_category_ids = False
                rec.blacklist_category_ids = False
            elif model == "product.category":
                rec.whitelist_product_ids = False
                rec.blacklist_product_ids = False
                rec.whitelist_template_ids = False
                rec.blacklist_template_ids = False

    @api.depends("assortment_filter_id")
    def _compute_name_and_price(self):
        res = super()._compute_name_and_price()
        for rec in self:
            if rec.assortment_filter_id:
                rec.name = rec.assortment_filter_id.name
        return res

    @classmethod
    def _get_blacklisted_fields(cls):
        return models.MAGIC_COLUMNS + [cls.CONCURRENCY_CHECK_FIELD] + BLACKLIST_FIELDS

    def _update_assortment_items(self):
        """
        Update the pricelist with current assortment:
        - Prepare values for new assortment items;
        - Delete no longer included items.
        - Create new assortment items;

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
        self._delete_no_longer_included_items()
        self._create_new_assortment_items()
        return True

    def _delete_no_longer_included_items(self):
        """
        Delete no longer included items from pricelist
        """
        self._get_related_items().unlink()

    def _create_new_assortment_items(self):
        """
        Create new assortment items in pricelist
        """
        item_obj = self.env["product.pricelist.item"]
        items_values, item_ids = self._get_pricelist_item_values()
        for item_value in items_values:
            item_obj.create(item_value)

    def _get_pricelist_values(self, items, default_values, applied_on, field_name):
        list_values = []
        item_ids = set()
        items |= (
            self.assortment_filter_id[f"whitelist_{field_name}_ids"]
            + self[f"whitelist_{field_name}_ids"]
        )
        items -= (
            self.assortment_filter_id[f"blacklist_{field_name}_ids"]
            + self[f"blacklist_{field_name}_ids"]
        )
        for item in items:
            values = default_values.copy()
            values.update(
                {
                    "pricelist_id": self.pricelist_id.id,
                    "assortment_item_id": self.id,
                    "applied_on": applied_on,
                    field_name: item.id,
                }
            )
            item_ids.add(item.id)
            list_values.append(values)
        return list_values, item_ids

    def _get_pricelist_category_values(self, categs, default_values):
        return self._get_pricelist_values(
            categs, default_values, "2_product_category", "categ"
        )

    def _get_pricelist_template_values(self, templates, default_values):
        return self._get_pricelist_values(
            templates, default_values, "1_product", "product_tmpl"
        )

    def _get_pricelist_product_values(self, products, default_values):
        return self._get_pricelist_values(
            products, default_values, "0_product_variant", "product"
        )

    def _get_pricelist_item_values(self):
        """
        Get a list of values to create new product.pricelist.item
        :return: list of dict
        """
        self.ensure_one()
        items = self._get_items_from_assortment()
        # fields to ignore to create pricelist item
        blacklist = self._get_blacklisted_fields()
        blacklist.extend(["assortment_filter_id", "pricelist_item_ids"])
        default_values = {
            k: self._fields.get(k).convert_to_write(self[k], self)
            for k in self._fields.keys()
            if k not in blacklist
        }
        return getattr(
            self,
            f"_get_pricelist_{self.assortment_filter_id.model_id.split('.')[1]}_values",
        )(items, default_values)

    def _get_items_from_assortment(self):
        domain = self.assortment_filter_id._get_eval_domain()
        model_obj = self.env[self.assortment_filter_id.model_id]
        if hasattr(model_obj, "company_id"):
            if self.company_id:
                domain = expression.AND(
                    [domain, [("company_id", "in", (self.company_id.id, False))]]
                )
            else:
                domain = expression.AND([domain, [("company_id", "=", False)]])
        products = self.env[self.assortment_filter_id.model_id].search(domain)
        return products

    def _get_related_items(self):
        domain = [("assortment_item_id", "in", self.ids)]
        return self.env["product.pricelist.item"].search(domain)

    @api.constrains("product_id", "product_tmpl_id", "categ_id")
    def _check_product_consistency(self):
        for rec in self:
            if any((rec.product_id, rec.product_tmpl_id, rec.categ_id)):
                raise ValidationError(
                    _(
                        "You can't set a product, a product template or a "
                        "category on an assortment item."
                    )
                )
