# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import Domain


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    @api.depends_context("location_id")
    def _product_qty(self):
        if location := self.env.context.get("location_id"):
            for lot in self:
                quants = lot.quant_ids.filtered_domain(
                    [("location_id", "child_of", int(location))]
                )
                lot.product_qty = sum(quants.mapped("quantity"))
        else:
            return super()._product_qty()

    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        if location := self.env.context.get("location_id"):
            domain = Domain.AND(
                [domain, [("quant_ids.location_id", "=", int(location))]]
            )
        return super()._search(
            domain, offset=offset, limit=limit, order=order, **kwargs
        )
