# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
import odoo.addons.decimal_precision as dp
from odoo.tools import float_round


class PriceRecalculationLine(models.AbstractModel):
    """Price Recalculation Line"""
    _name = 'price.recalculation.line'
    _description = __doc__

    product_id = fields.Many2one('product.product', 'Product', readonly=1)
    qty = fields.Float(
        'Qty', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True)
    price_subtotal = fields.Float(
        'Total ex Tax', digits=dp.get_precision('Account'))
    price_unit = fields.Float(
        'Unit Price', required=True,
        digits=dp.get_precision('Product Price'))
    price_total = fields.Float(
        'Total inc Tax', digits=dp.get_precision('Account'))
    effective_tax_rate = fields.Float('Effective Tax Rate', readonly=True)

    @api.onchange('price_total')
    def _onchange_total(self):
        # Note: Required to avoid div by zero errors
        # due to upstream bug not honoring create="0"
        # https://github.com/odoo/odoo/issues/19053
        if not (self.effective_tax_rate and self.qty):
            return
        price_subtotal = self.price_total / (1 + self.effective_tax_rate)
        self.price_unit = float_round(price_subtotal / self.qty,
                                      self._context.get('precision', 2))
        self.price_subtotal = self.price_unit * self.qty
        self.total = self.price_subtotal * (1 + self.effective_tax_rate)

    @api.onchange('price_subtotal')
    def _onchange_subtotal(self):
        # Note: Required to avoid div by zero errors
        # due to upstream bug not honoring create="0"
        # https://github.com/odoo/odoo/issues/19053
        if not self.qty:
            return
        self.price_unit = float_round(self.price_subtotal / self.qty,
                                      self._context.get('precision', 2))
        self.price_subtotal = self.price_unit * self.qty
        self.total = self.price_subtotal * (1 + self.effective_tax_rate)
