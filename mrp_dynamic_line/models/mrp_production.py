# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, _

_logger = logging.Logger(__name__)


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def _generate_raw_moves(self, exploded_lines):
        lines_done = []
        for bom_line, line_fields in exploded_lines:
            for xform in bom_line.xform_ids.filtered(
                lambda bl: bl.application_point == "move"
            ).sorted("sequence"):
                try:
                    func = getattr(
                        self, "_generate_raw_move_%s" % xform.technical_name
                    )
                    bom_line, line_fields = func(bom_line, line_fields)
                except AttributeError:
                    _logger.error(
                        _("No function found with name _generate_raw_move_%s")
                        % xform.technical_name
                    )
                if not bom_line:
                    # Its deleted so nothing more to xform
                    break
            bom_line and lines_done.append((bom_line, line_fields))
        exploded_lines = lines_done
        return super()._generate_raw_moves(exploded_lines)

    @api.multi
    def _update_raw_move(self, bom_line, line_data):
        self.ensure_one()
        for xform in bom_line.xform_ids.filtered(
            lambda bl: bl.application_point == "move"
        ).sorted("sequence"):
            bom_line_id = bom_line.id
            try:
                func = getattr(
                    self, "_generate_raw_move_%s" % xform.technical_name
                )
                bom_line, line_fields = func(bom_line, line_data)
            except AttributeError:
                _logger.error(
                    _("No function found with name _generate_raw_move_%s")
                    % xform.technical_name
                )
            if not bom_line:
                # Its deleted so nothing more to xform
                move = self.move_raw_ids.filtered(
                    lambda x: (
                        x.bom_line_id.id == bom_line_id
                        and x.state not in ("done", "cancel")
                    )
                )
                if move:
                    move._action_cancel()
                    move.unlink()
                break
        return bom_line and super()._update_raw_move(bom_line, line_data)

    @api.multi
    def button_plan(self):
        if len(self) == 1 and "product_id" in self._context:
            super().button_plan()
        else:
            for order in self:
                super(MrpProduction, order).with_context(
                    product_id=order.product_id.id
                ).button_plan()
