# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        """Prevent annoying error when user changes picking type"""
        if self.picking_type_id:
            self.operating_unit_id = self.picking_type_id.warehouse_id.operating_unit_id
            self.requesting_operating_unit_id = (
                self.picking_type_id.warehouse_id.operating_unit_id
            )
