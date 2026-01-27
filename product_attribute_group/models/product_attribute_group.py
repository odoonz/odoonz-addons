# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeGroup(models.Model):
    _name = "product.attribute.group"
    _description = "Product Attribute Group"
    _order = "attribute_id, name asc"

    name = fields.Char(required=True)
    attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Product Attribute",
        ondelete="restrict",
        required=True,
    )
    value_ids = fields.Many2many(
        comodel_name="product.attribute.value", string="Product Attribute Values"
    )
    attribute_line_ids = fields.Many2many(
        comodel_name="product.template.attribute.line",
        string="Product Attributes",
        copy=False,
    )

    _uniq_name = models.Constraint(
        'unique(name)',
        "The attribute group name must be unique",
    )

    def write(self, values):
        """Update template attribute lines when value_ids change."""
        result = super().write(values)

        if "value_ids" in values:
            attribute_lines = self.env["product.template.attribute.line"].search(
                [("attr_group_ids", "in", self.ids)]
            )

            if attribute_lines:
                for line in attribute_lines:
                    new_value_ids = line.attr_group_ids.value_ids
                    line.write({"value_ids": [(6, 0, new_value_ids.ids)]})

        return result

    def copy(self, default=None):
        """
        Override copy to ensure the copy is distinguishable
        from original and is not assigned to any products.
        :param default:
        :return: newly created record
        """
        default = dict(default or {})
        default["name"] = f"{self.name} (Copy)"
        return super().copy(default=default)

    def button_copy(self):
        """
        Allows duplication of attribute groups from tree view
        :return: refreshed view of attribute groups
        """
        self.ensure_one()
        self.copy()
        return self.env["ir.actions.act_window"]._for_xml_id(
            "product_attribute_group.product_attribute_group_act_window"
        )
