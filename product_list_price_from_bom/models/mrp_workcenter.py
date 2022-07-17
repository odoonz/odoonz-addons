# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    def _get_default_labour_price(self):
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("product_list_price_from_bom.default_labour_rate", 110.0)
        )

    price_hour = fields.Float(
        string="Price per hour",
        help="Used when calculating list price from BoM",
        default=_get_default_labour_price,
        digits="Product Price",
    )
