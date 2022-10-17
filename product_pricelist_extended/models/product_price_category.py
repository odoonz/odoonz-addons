# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPriceCategory(models.Model):
    """Product Price Category"""

    _name = "product.price.category"
    _description = __doc__

    name = fields.Char(string="Category Name", required=True)
    description = fields.Text("Description", required=True)
    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template", string="Products"
    )
    product_ids = fields.Many2many(comodel_name="product.product", string="Variants")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tmpl_price_categ_ids = fields.Many2many(
        comodel_name="product.price.category", string="Product Price Categories"
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    price_categ_ids = fields.Many2many(
        comodel_name="product.price.category", string="Variant Price Categories"
    )
