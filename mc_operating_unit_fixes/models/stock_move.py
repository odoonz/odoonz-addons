from odoo import _, api, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.constrains("picking_id", "location_id", "location_dest_id")
    def _check_stock_move_operating_unit(self):
        for stock_move in self:
            ou_pick = stock_move.picking_id.operating_unit_id or False
            ou_src = stock_move.operating_unit_id or False
            ou_dest = stock_move.operating_unit_dest_id or False
            one_ou = not ou_pick or (ou_src or ou_dest)
            if (
                ou_src
                and ou_pick
                and one_ou
                and (ou_src not in [ou_pick, False])
                and (ou_dest not in [ou_pick, False])
            ):
                raise UserError(
                    _(
                        "Configuration error. The Stock moves must "
                        "be related to a location (source or destination) "
                        "that belongs to the requesting Operating Unit."
                    )
                )
