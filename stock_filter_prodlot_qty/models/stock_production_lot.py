# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockProductionLot(models.Model):

    _inherit = "stock.lot"

    def _product_qty(self):
        for lot in self:
            if lot.env.context.get("location_id"):
                lot.product_qty = lot.product_id.with_context(
                    location=lot.env.context.get("location_id"), lot_id=lot.id
                ).qty_available
            else:
                super()._product_qty()

    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        if not self.env.context.get("location_id"):
            return super()._search(
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )
        results = self.env["stock.production.lot"]
        while len(results) < (limit or 1):
            result = super()._search(
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )
            for r in self.browse(result):
                if r.with_context(
                    location=self.env.context.get("location_id")
                ).product_qty:
                    results |= r
            if not limit or len(result) < limit:
                break
            offset += limit
        return results.ids
