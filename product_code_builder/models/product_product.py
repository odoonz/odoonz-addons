# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .helper_methods import render_default_code


class ProductProduct(models.Model):
    _inherit = "product.product"

    manual_code = fields.Boolean(string="Manual code", default=False)

    @api.model_create_multi
    def create(self, values):
        products = super().create(values)
        for product in products:
            if product.reference_mask:
                render_default_code(product, product.reference_mask)
        return products

    @api.onchange("default_code")
    def onchange_default_code(self):
        self.manual_code = bool(self.default_code)
