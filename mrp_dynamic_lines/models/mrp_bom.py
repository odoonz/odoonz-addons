# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    def explode(self, product, quantity, picking_type=False):
        boms_done, orig_lines_done = super(MrpBom, self).explode(
            product, quantity, picking_type=picking_type)
        lines_done = []
        for bom_line, orig_line in orig_lines_done:
            bom_line = bom_line.with_context(
                product_id=orig_line['product'].id)
            lines_done.append((bom_line, orig_line))
        return boms_done, lines_done
