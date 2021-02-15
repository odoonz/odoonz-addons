# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    required_value_ids = fields.Many2many(
        comodel_name="product.template.attribute.value",
        relation="bom_line_req_attr_val_rel",
        string="Required Values",
        help="Require the raw material to have these attribute values",
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
    )
    # Note: Just changing a useless help message here
    bom_product_template_attribute_value_ids = fields.Many2many(
        help="Only apply this line if the manufactured product contains"
        "these attribute values."
    )

    xform_ids = fields.Many2many("bom.line.xform", string="Transformations")
