# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(self, *args):
        context = dict(self._context)
        if context.get("reforce_ref") and "forced_ref" in context:
            context["forced_ref"] = (
                "Revaluation of %s (FIFO)" % self.picking_id.name
                or self.product_id.default_code
            )
        return super(
            StockMove, self.with_context(**context)
        )._generate_valuation_lines_data(*args)
