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
