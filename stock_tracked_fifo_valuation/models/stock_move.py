# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_in_base_domain(self, company_id=False):
        domain = [
            ("state", "=", "done"),
            ("location_id.usage", "!=", "internal"),
            (
                "location_dest_id.company_id",
                "=",
                company_id or self.env.user.company_id.id,
            ),
            ("location_dest_id.usage", "=", "internal"),
        ]
        return domain

    @api.model
    def _get_all_base_domain(self, company_id=False):
        domain = [
            ("state", "=", "done"),
            "|",
            "&",
            "&",
            ("location_id.usage", "!=", "internal"),
            (
                "location_dest_id.company_id",
                "=",
                company_id or self.env.user.company_id.id,
            ),
            ("location_dest_id.usage", "=", "internal"),
            "&",
            "&",
            ("location_id.company_id", "=", company_id or self.env.user.company_id.id),
            ("location_id.usage", "=", "internal"),
            ("location_dest_id.usage", "!=", "internal"),
        ]
        return domain

    @api.model
    def _run_fifo(self, move, quantity=None):
        if move.has_tracking != "none":
            move = move.with_context(
                lots={
                    ml.lot_id.id: ml.qty_done for ml in move.move_line_ids if ml.lot_id
                }
            )
        super()._run_fifo(move, quantity=quantity)


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        """Overide of funtction
        If we are increasing qty we need to use the fifo price for that lot
        rather than standard_price. If the lot is already consumed it will
        default to the oldest availalbe standard price
        """
        values = super()._get_move_values(qty, location_id, location_dest_id, out)
        if (
            self.product_qty > self.theoretical_qty
            and self.product_id.cost_method == "fifo"
            and self.prod_lot_id
        ):
            candidates = self.product_id.with_context(
                lots={self.prod_lot_id: qty}
            )._get_fifo_candidates_in_move_with_company(
                move_company_id=self.inventory_id.company_id.id
            )
            if candidates:
                values["price_unit"] = candidates[0].price_unit
        return values
