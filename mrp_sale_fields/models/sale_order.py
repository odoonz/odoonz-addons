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
            """SELECT sol.order_id, COUNT(sm.created_production_id) 
        FROM stock_move sm 
        LEFT JOIN sale_order_line sol ON sm.sale_line_id = sol.id
        LEFT JOIN mrp_production mrp ON mrp.id = sm.created_production_id
        WHERE sm.sale_line_id IS NOT NULL 
          AND sm.created_production_id IS NOT NULL 
          AND sol.order_id IN %s 
          AND mrp.state != 'cancel'
        GROUP BY sol.order_id""",
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
