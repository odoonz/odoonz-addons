# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SalePriceRecalculationLine(models.TransientModel):
    """Sale Price Recalculation Line"""

    _inherit = "price.recalculation.line"
    _name = "sale.price.recalculation.line"
    _description = __doc__

    name = fields.Many2one(comodel_name="sale.order.line", readonly=True)
    price_recalculation_id = fields.Many2one(
        comodel_name="sale.price.recalculation", string="Price Recalculation"
    )
    discount = fields.Float("Discount (%)", digits=dp.get_precision("Discount"))

    @api.onchange("price_total")
    def _onchange_total(self):
        self.discount = 0.0
        return super()._onchange_total()

    @api.onchange("price_subtotal")
    def _onchange_subtotal(self):
        self.discount = 0.0
        return super()._onchange_subtotal()

    @api.onchange("price_unit", "discount")
    def _onchange_price(self):
        self.price_subtotal = (
            self.qty * self.price_unit * ((100.0 - self.discount) / 100.0)
        )
        self.price_total = self.price_subtotal * (1 + self.effective_tax_rate)
