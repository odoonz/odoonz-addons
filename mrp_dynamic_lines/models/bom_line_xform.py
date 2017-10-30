# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BomLineXform(models.Model):
    """Bom Line Dynamic Transformations"""
    _name = 'bom.line.xform'
    _description = __doc__

    name = fields.Char()
    technical_name = fields.Char(
        help="Will correspond to a function e.g. match_attributes"
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text()
    sequence = fields.Integer(default=5)
    application_point = fields.Selection([('explode', 'BoM Explosion'),
                                          ('move', 'Raw Move Generation')])

    bom_line_ids = fields.Many2many('mrp.bom.line')
