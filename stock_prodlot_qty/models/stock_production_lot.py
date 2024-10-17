# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockProductionLot(models.Model):

    _inherit = "stock.lot"

    def name_get(self):
        res = super().name_get()
        if self.env.context.get("show_qty") and res:
            res = self.browse([r[0] for r in res]).mapped(
                lambda r: (r.id, (r.name or "") + "(%.0f) " % r.product_qty)
            )
        return res
