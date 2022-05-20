# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    """product pricelist item - little changes to enable m2m product_ids"""

    _inherit = "product.pricelist.item"
    _order = "applied_on, min_quantity desc, categ_id desc, name, id"

    name = fields.Char(store=True)
    price = fields.Char(store=True)

    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="pricelist_item_product_rel",
        column1="pricelist_item_id",
        column2="prod_id",
        string="Products",
    )
    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="pricelist_item_tmpl_rel",
        column1="pricelist_item_id",
        column2="tmpl_id",
        string="Templates",
    )
    price_categ_id = fields.Many2one(
        comodel_name="product.price.category", string="Pricing Category"
    )

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        super()._get_pricelist_item_name_price()
        for item in self:
            if item.price_categ_id and item.applied_on == "2_product_category":
                item.name = _("Price Category: %s") % item.price_categ_id.display_name
            elif item.product_tmpl_ids and item.applied_on == "1_product":
                item.name = _("Product: %s") % (
                    ",".join(item.product_tmpl_ids.mapped("display_name"))
                )
            elif item.product_ids and item.applied_on == "0_product_variant":
                item.name = _("Variant: %s") % (
                    ",".join(
                        self.env["product.product"]
                        .with_context(display_default_code=False)
                        .browse(item.product_ids.ids)
                        .mapped("display_name")
                    )
                )

    @api.constrains(
        "product_ids",
        "product_tmpl_ids",
        "price_categ_id",
        "product_id",
        "product_tmpl_id",
        "categ_id",
    )
    def _check_product_consistency(self):
        """
            Rewrite this validation function:
            only one field should be set
        """
        for item in self:
            if item.applied_on == "2_product_category" and bool(item.categ_id) == bool(
                item.price_categ_id
            ):
                raise ValidationError(
                    _(
                        "Please specify product category or price category for which "
                        "this rule should be applied"
                    )
                )
            elif item.applied_on == "1_product" and bool(item.product_tmpl_id) == bool(
                item.product_tmpl_ids
            ):
                raise ValidationError(
                    _(
                        "Please specify the product for which "
                        "this rule should be applied"
                    )
                )
            elif item.applied_on == "0_product_variant" and bool(
                item.product_id
            ) == bool(item.product_ids):
                raise ValidationError(
                    _(
                        "Please specify the product variant for which "
                        "this rule should be applied"
                    )
                )

    @api.onchange("applied_on")
    def _onchange_applied_on(self):
        for item in self:
            if not item.applied_on or self.env.context.get("default_applied_on", False):
                return
            if item.applied_on != "0_product_variant":
                item.product_id = False
                item.product_ids = False
            if item.applied_on != "1_product":
                item.product_tmpl_id = False
                item.product_tmpl_ids = False
            if item.applied_on != "2_product_category":
                item.categ_id = False
                item.price_categ_id = False

    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        for item in self:
            if item.categ_id:
                item.price_categ_id = False

    @api.onchange("price_categ_id")
    def _onchange_price_categ_id(self):
        for item in self:
            if item.price_categ_id:
                item.categ_id = False
