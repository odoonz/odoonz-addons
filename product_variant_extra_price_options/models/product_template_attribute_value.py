# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateAttributeValue(models.Model):

    _inherit = "product.template.attribute.value"

    price_extra_method = fields.Selection(related="attribute_id.price_extra_method")
    price_multiply_extra = fields.Float(digits="Product Price", default=1)
    price_multiply_attributes = fields.Many2many(
        "product.attribute", string="Apply only to these attributes"
    )
    price_extra_depends_ids = fields.One2many(
        comodel_name="attribute.value.price.extra", inverse_name="ptav_id"
    )

    def _pre_calc_price_extra_depends(self, price_extra_dict, ptavs):
        price_extra_base = price_extra_dict[self.attribute_id.id]
        for price_extra in self.price_extra_depends_ids:
            if price_extra.dependent_ptav_id in ptavs:
                price_extra_base += price_extra.price_extra
        price_extra_dict[self.attribute_id.id] = price_extra_base
        return price_extra_dict

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


class AttributeValuePriceExtra(models.Model):
    _name = "attribute.value.price.extra"
    _description = "Dependent Price Extra"

    ptav_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        string="Applies To",
        required=True,
    )
    price_extra = fields.Float(digits="Product Price")
    dependent_ptav_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        string="Depends On",
        domain="[('product_tmpl_id', '=', product_tmpl_id), "
        "('ptav_active', '=', True)]",
    )
    product_tmpl_id = fields.Many2one(
        related="ptav_id.product_tmpl_id",
        string="Product Template",
        ondelete="cascade",
        required=True,
        index=True,
    )
