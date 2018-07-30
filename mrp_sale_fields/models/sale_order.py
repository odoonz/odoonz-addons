# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    production_count = fields.Integer(
        string="Production Orders", compute="_compute_production_ids"
    )

    @api.multi
    def _compute_production_ids(self):
        production_data = self.env["mrp.production"].read_group(
            domain=[("sale_id", "in", self.ids)],
            fields=["sale_id"],
            groupby=["sale_id"],
        )
        mapped_data = dict(
            [
                (data["sale_id"][0], data["sale_id_count"])
                for data in production_data
            ]
        )
        for order in self:
            order.production_count = mapped_data.get(order.id, 0)

    @api.multi
    def action_view_production(self):
        """
        This function returns an action that display existing production orders
        of given sales order ids.
        """
        self.ensure_one()
        action = self.env.ref("mrp.mrp_production_action").read()[0]
        action["domain"] = [("sale_id", "=", self.id)]
        return action
