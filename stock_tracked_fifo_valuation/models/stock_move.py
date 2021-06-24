# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        for move in self.filtered(lambda s: s.product_id.tracking != "none"):
            move.with_context(lots=move.lot_ids.ids)
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _get_price_unit(self):
        """Override for case of inventory adjustments upwards of existing svl"""
        self.ensure_one()
        price_unit = super()._get_price_unit()
        if (
            not self.purchase_line_id
            and self.product_id.cost_method == "fifo"
            and len(self.lot_ids) == 1
        ):
            # lots should have same cost regardless if using actual
            candidates = (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", self.id),
                        ("lot_ids", "in", self.lot_ids.ids),
                        ("quantity", ">", 0),
                        ("value", ">", 0),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
            )
            if candidates:
                price_unit = candidates[0].unit_cost
        return price_unit
