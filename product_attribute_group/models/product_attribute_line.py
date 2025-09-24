# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    attr_group_ids = fields.Many2many(
        comodel_name="product.attribute.group",
        string="Attribute Groups",
        domain="[('attribute_id', '=', attribute_id)]",
    )

    value_ids = fields.Many2many(
        compute="_compute_value_ids", store=True, readonly=False
    )

    @api.depends("attr_group_ids", "attr_group_ids.value_ids", "attribute_id")
    def _compute_value_ids(self):
        """
        Mostly eye candy - we update the display to show the new values
        when the attribute group changes - however as the field is
        readonly in the UI it won't write so we handle properly in write
        :return:
        """
        if self.attr_group_ids:
            self.value_ids = self.attr_group_ids.value_ids
            if self._context.get("create_product_product", True):
                self._update_product_template_attribute_values()
