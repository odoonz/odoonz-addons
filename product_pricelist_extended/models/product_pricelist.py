# Copyright 2014 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: skip-file
# flake8: noqa
# we copy from odoo so easier to keep in line for modifications


from odoo import fields, models


class ProductPricelist(models.Model):
    """
    Inherited class - to change pricing calculation and options
    """

    _inherit = "product.pricelist"

    base_pricelist = fields.Boolean(
        string="Can be used as a base pricelist",
        default=False,
    )
