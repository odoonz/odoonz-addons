# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_mrp_production_count(self):
        super()._compute_mrp_production_count()
        for sale in self:
            active_mrp_orders = sale.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.filtered(
                lambda o: o.state != "cancel"
            )
            sale.mrp_production_count = len(active_mrp_orders)

    def action_view_mrp_production(self):
        action = super().action_view_mrp_production()
        action["domain"].append(("sale_id", "=", self.id))
        return action
