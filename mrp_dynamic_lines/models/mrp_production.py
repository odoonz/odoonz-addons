# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, _

_logger = logging.Logger(__name__)


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    def _generate_raw_moves(self, exploded_lines):
        lines_done = []
        for bom_line, line_fields in exploded_lines:
            for xform in bom_line.xform_ids.filtered(
                    lambda bl: bl.application_point == 'move').sorted(
                    'sequence'):
                func = getattr(self, '_generate_raw_move_%s' %
                               xform.technical_name)
                if func:
                    bom_line, line_fields = func(bom_line, line_fields)
                else:
                    _logger.error(
                        _('No function found with name _explode_%s') %
                        xform.technical_name)
                if not bom_line:
                    # Its deleted so nothing more to xform
                    break
            bom_line and lines_done.append((bom_line, line_fields))
        exploded_lines = lines_done
        return super(MrpProduction, self)._generate_raw_moves(exploded_lines)
