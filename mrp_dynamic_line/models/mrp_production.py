# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()
        moves = [m for m in moves if m["product_uom_qty"]]
        return moves

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        if bom_line:
            if "product" in bom_line.env.context:
                product_id = bom_line.env.context["product"]
            for xform in bom_line.xform_ids.filtered(
                lambda bl: bl.application_point == "move"
            ).sorted("sequence"):
                try:
                    func = getattr(self, f"_get_move_raw_{xform.technical_name}")
                except AttributeError:
                    _logger.error(
                        _(
                            "No function found with name _get_move_raw_%(name)s",
                            name=xform.technical_name,
                        )
                    )
                else:
                    (
                        product_id,
                        product_uom_qty,
                        product_uom,
                        operation_id,
                        bom_line,
                    ) = func(
                        product_id, product_uom_qty, product_uom, operation_id, bom_line
                    )
        return super()._get_move_raw_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            bom_line=bom_line,
        )

    def _update_raw_moves(self, factor):
        """Determine new quantity from transformations if any"""
        self.ensure_one()
        update_info = []

        # Re-explode BOM with new qty as lines may be added or removed
        self.product_qty = float_round(
            self.product_qty * factor, precision_rounding=self.product_uom_id.rounding
        )
        _bom, lines_done = self.bom_id.explode(
            self.product_id, self.product_qty, picking_type=self.picking_type_id
        )
        lines_done = {line[0]: line[1] for line in lines_done}

        for move in self.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        ):
            old_qty = move.product_uom_qty

            bom_line = move.bom_line_id
            bom_vals = lines_done.pop(bom_line)
            xforms = bom_line.xform_ids.filtered(
                lambda bl: bl.application_point == "move"
            ).sorted("sequence")
            if not bom_vals:
                # If there are no bom_vals then we have removed the bom line.
                # We need to remove the move and any related moves
                update_info.append((move, old_qty, 0))
                move.write({"product_uom_qty": 0})
                continue

            if xforms:
                new_qty = bom_vals["qty"]
                for xform in xforms:
                    try:
                        func = getattr(self, f"_get_move_raw_{xform.technical_name}")
                    except AttributeError:
                        _logger.error(
                            _(
                                "No function found with name _get_move_raw_%(name)s",
                                name=xform.technical_name,
                            )
                        )
                    else:
                        new_qty = func(
                            move.product_id,
                            new_qty,
                            move.product_uom,
                            move.operation_id,
                            bom_line,
                        )[1]
            else:
                new_qty = float_round(
                    old_qty * factor,
                    precision_rounding=move.product_uom.rounding,
                    rounding_method="UP",
                )

            move.write({"product_uom_qty": new_qty})
            update_info.append((move, old_qty, new_qty))

        # These should be the unprocessed ones
        for bom_line, bom_vals in lines_done.items():
            # We need the specific context of the key to get the product
            product = bom_line.env.context.get("product", bom_line.product_id)
            move_vals = self._get_move_raw_values(
                product,
                bom_vals["qty"],
                bom_line.product_uom_id,
                bom_line.operation_id.id,
                bom_line,
            )
            if move_vals["product_uom_qty"] == 0.0:
                continue
            move = self.env["stock.move"].create(move_vals)
            update_info.append((move, 0, move.product_uom_qty))

        return update_info

    def button_plan(self):
        if len(self) == 1 and "product_id" in self.env.context:
            super().button_plan()
        else:
            for order in self:
                super(MrpProduction, order).with_context(
                    product_id=order.product_id.id
                ).button_plan()
        return True
