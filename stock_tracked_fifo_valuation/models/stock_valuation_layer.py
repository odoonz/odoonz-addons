from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    lot_ids = fields.Many2many(
        "stock.production.lot",
        compute="_compute_lot_ids",
        string="Serial Numbers",
        store=True,
    )

    @api.depends("stock_move_id")
    def _compute_lot_ids(self):
        for svl in self:
            svl.lot_ids = svl.stock_move_id.lot_ids

    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super().search(args, offset=offset, limit=limit, order=order, count=count)
        if res and self._context.get("lots"):
            new_res = self.browse()
            for svl in res:
                if svl.product_id.tracking != "none":
                    for lot in svl.lot_ids.ids:
                        if lot in self._context["lots"]:
                            new_res |= svl
                            break
            new_res |= res - new_res
            res = new_res
        return res
