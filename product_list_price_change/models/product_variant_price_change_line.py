# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductVariantPriceChangeLine(models.Model):

    _name = "product.variant.price.change.line"
    _description = "Product Variant Price Change Line"
    _rec_name = "product_tmpl_attribute_value_id"
    _order = "effective_date desc, id"

    product_tmpl_attribute_value_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        required=True,
        states={'cancel': [('readonly', True)], 'future': [('readonly', True)], 'live': [('readonly', True)]},
    )
    price_change_id = fields.Many2one(
        string="Price Change",
        comodel_name="product.price.change",
        required=True,
        states={'cancel': [('readonly', True)], 'future': [('readonly', True)], 'live': [('readonly', True)]},
    )
    price_extra = fields.Float(
        "Price Extra",
        required=True,
        digits=dp.get_precision("Product Price"),
        help="Extra Price for attribute.",
        states={'cancel': [('readonly', True)], 'future': [('readonly', True)], 'live': [('readonly', True)]},
    )
    state = fields.Selection(related="price_change_id.state", store=True)
    effective_date = fields.Date(related="price_change_id.effective_date", store=True)
