# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    production_count = fields.Integer(
        string="Production Orders", compute="_compute_production_ids"
    )

    def _compute_production_ids(self):
        self._cr.execute(
            """SELECT COUNT(mrp.sale_id)
        FROM mrp_production mrp
        WHERE mrp.sale_id IN %s
          AND mrp.state != 'cancel'
        GROUP BY mrp.sale_id""",
            (tuple(self.ids),),
        )
        production_data = self._cr.fetchall()
        if production_data:
            mapped_data = dict(production_data)
            for order in self.browse(mapped_data.keys()):
                order.production_count = mapped_data.get(order.id, 0)

    def action_view_production(self):
        """
        This function returns an action that display existing production orders
        of given sales order ids.
        """
        self.ensure_one()
        action = self.env.ref("mrp.mrp_production_action").read()[0]
        action["domain"] = [("sale_id", "=", self.id)]
        return action
