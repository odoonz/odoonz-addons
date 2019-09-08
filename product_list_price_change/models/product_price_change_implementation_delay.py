# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPriceChangeImplementationDelay(models.Model):

    _name = "product.price.change.implementation_delay"
    _description = "Product Price Change Implementation Delay"
    _order = "effective_date desc"

    name = fields.Char(required=True)
    effective_date = fields.Date(required=True)
    included_categories = fields.Many2many(
        comodel_name="res.partner.category",
        relation="price_change_impl_delay_res_partner_category_rel",
        required=True,
    )
    price_change_id = fields.Many2one(
        string="Price Change", comodel_name="product.price.change", required=True
    )
