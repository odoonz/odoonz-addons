# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    external_reference = fields.Char(
        string="Supplier Reference",
        help="Supplier Reference for the primary supplier of this product.",
    )
