# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    name = fields.Char(translate=False)
    description = fields.Text(translate=False)
    description_purchase = fields.Text(translate=False)
    description_sale = fields.Text(translate=False)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    name = fields.Char(translate=False)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    name = fields.Char(translate=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    name = fields.Char(translate=False)


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    name = fields.Char(translate=False)
