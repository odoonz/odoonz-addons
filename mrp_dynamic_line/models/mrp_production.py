# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models

_logger = logging.Logger(__name__)


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
            if "product" in bom_line._context:
                product_id = bom_line._context["product"]
            for xform in bom_line.xform_ids.filtered(
                lambda bl: bl.application_point == "move"
            ).sorted("sequence"):
                try:
                    func = getattr(self, "_get_move_raw_%s" % xform.technical_name)
                except AttributeError:
                    _logger.error(
                        _("No function found with name _get_move_raw_%s")
                        % xform.technical_name
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

    def _update_raw_move(self, bom_line, line_data):
        self.ensure_one()
        for xform in bom_line.xform_ids.filtered(
            lambda bl: bl.application_point == "move"
        ).sorted("sequence"):
            bom_line_id = bom_line.id
            try:
                func = getattr(self, "_generate_raw_move_%s" % xform.technical_name)
            except AttributeError:
                _logger.error(
                    _("No function found with name _generate_raw_move_%s")
                    % xform.technical_name
                )
            else:
                bom_line, line_data = func(bom_line, line_data)
            if not bom_line:
                # Its deleted so nothing more to xform
                move = self.move_raw_ids.filtered(
                    lambda x: (
                        x.bom_line_id.id == bom_line_id
                        and x.state not in ("done", "cancel")
                    )
                )
                if move:
                    old_qty = move[0].product_uom_qty
                    move[0].write({"product_uom_qty": 0.0})
                    return move[0], old_qty, 0
                return self.env["stock.move"], 0, 0
        return bom_line and super()._update_raw_move(bom_line, line_data)

    def button_plan(self):
        if len(self) == 1 and "product_id" in self._context:
            super().button_plan()
        else:
            for order in self:
                super().with_context(product_id=order.product_id.id).button_plan()
