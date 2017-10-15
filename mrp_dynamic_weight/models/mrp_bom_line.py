# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):

    _inherit = 'mrp.bom.line'

    scale_weight = fields.Boolean(
        string='Scale Weight',
        help='Scale the line quantity by weight of variant',
    )

    @api.constrains('scale_weight')
    def check_uom_id(self):
        if self.scale_weight and self.product_uom_id != self.env.ref(
                'product.product_uom_kgm'):
            raise ValidationError(_('Scale weight only works for '
                                    'raw materials measured in kg.'))

    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        if self.product_uom_id != self.env.ref(
                'product.product_uom_kgm'):
            self.scale_weight = False
