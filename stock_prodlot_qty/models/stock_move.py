from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        action = super().action_show_details()
        if action and "context" in action:
            action["context"]["show_qty"] = True
        return action
