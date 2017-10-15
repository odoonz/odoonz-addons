# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchasePriceRecalculationLine(models.TransientModel):
    """Purchase Price Recalculation Line"""
    _inherit = 'price.recalculation.line'
    _name = 'purchase.price.recalculation.line'
    _description = __doc__

    name = fields.Many2one(comodel_name='purchase.order.line', readonly=True)
    price_recalculation_id = fields.Many2one(
        'purchase.price.recalculation', 'Price Recalculation')

    @api.onchange('price_unit')
    def _onchange_price(self):
        self.price_subtotal = self.qty * self.price_unit
        self.price_total = self.price_subtotal * (1 + self.effective_tax_rate)
