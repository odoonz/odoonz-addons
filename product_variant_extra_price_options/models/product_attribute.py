# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttribute(models.Model):

    _inherit = "product.attribute"

    price_extra_method = fields.Selection(
        [("price_extra", "Price Extra"), ("multiply_extra", "Multiply Attributes")],
        default="price_extra",
        required=True,
    )
