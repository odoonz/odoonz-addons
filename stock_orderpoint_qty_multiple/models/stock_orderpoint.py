# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    qty_multiple = fields.Integer(
        string="Quantity Multiple",
        default=0,
        help="When no replenishment unit is set, round the quantity to order "
        "up to a multiple of this value. Leave at 0 to keep the standard "
        "fallback (vendor unit or bill of materials unit). A replenishment "
        "unit takes priority over this value.",
    )

    _qty_multiple_check = models.Constraint(
        "CHECK(qty_multiple >= 0)",
        "Quantity Multiple must be greater than or equal to zero.",
    )

    @api.depends("qty_multiple")
    def _compute_qty_to_order_computed(self):
        # Recompute the quantity to order when the multiple changes.
        super()._compute_qty_to_order_computed()

    @api.depends("qty_multiple")
    def _compute_replenishment_uom_id_placeholder(self):
        # Show the multiple in the replenishment-unit placeholder.
        super()._compute_replenishment_uom_id_placeholder()

    def _get_replenishment_multiple_alternative(self, qty_to_order):
        # Use an in-memory unit so core rounding applies this multiple.
        self.ensure_one()
        if self.qty_multiple:
            return self.env["uom.uom"].new(
                {
                    "name": str(self.qty_multiple),
                    "relative_factor": self.qty_multiple,
                    "relative_uom_id": self.product_id.uom_id.id,
                }
            )
        return super()._get_replenishment_multiple_alternative(qty_to_order)
