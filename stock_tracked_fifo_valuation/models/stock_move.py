# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        if "lots" not in self.env.context:
            moves_tracked = self.filtered(
                lambda s: s.product_id.tracking != "none" and not s._context.get("lots")
            )
            self -= moves_tracked
            for move in moves_tracked:
                move.with_context(
                    lots=move.with_context(active_test=False).lot_ids.ids
                )._action_done(cancel_backorder=cancel_backorder)
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _get_price_unit(self):
        """Override for case of inventory adjustments upwards of existing svl"""
        self.ensure_one()
        price_unit = super()._get_price_unit()
        if (
            not self.purchase_line_id
            and self.product_id.cost_method == "fifo"
            and len(self.with_context(active_test=False).lot_ids) == 1
        ):
            # lots should have same cost regardless if using actual
            candidates = (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", self.id),
                        (
                            "lot_ids",
                            "in",
                            self.with_context(active_test=False).lot_ids.ids,
                        ),
                        ("quantity", ">", 0),
                        ("value", ">", 0),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
            )
            if candidates:
                price_unit = candidates[0].unit_cost
        return price_unit
