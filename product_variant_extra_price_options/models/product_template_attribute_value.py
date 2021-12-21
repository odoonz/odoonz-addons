# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateAttributeValue(models.Model):

    _inherit = "product.template.attribute.value"

    price_extra_method = fields.Selection(related="attribute_id.price_extra_method")
    price_multiply_extra = fields.Float(digits="Product Price", default=1)
    price_multiply_attributes = fields.Many2many(
        "product.attribute", string="Apply only to these attributes"
    )  # Needs domain

    def _calc_price_extra(self, price_extra_dict):
        return price_extra_dict

    def _calc_multiply_extra(self, price_extra_dict):
        attribute_ids = set(self.price_multiply_attributes.ids)
        multiple = self.price_multiply_extra
        new_price_extra_dict = price_extra_dict.copy()
        for attribute, price_extra in price_extra_dict.items():
            if not attribute_ids or attribute in attribute_ids:
                new_price_extra_dict[attribute] = price_extra * multiple
        return new_price_extra_dict
