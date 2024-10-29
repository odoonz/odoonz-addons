# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.api import readonly
from odoo.tools import float_round


class PriceRecalculationLine(models.AbstractModel):
    """Price Recalculation Line"""

    _name = "price.recalculation.line"
    _description = __doc__

    product_id = fields.Many2one("product.product", "Product", readonly=1)
    qty = fields.Float("Qty", digits="Product Unit of Measure", readonly=True)
    price_subtotal = fields.Float("Total ex Tax", digits="Account", inverse="_compute_price_subtotal", readonly=False)
    price_unit = fields.Float("Unit Price", required=True, digits="Product Price")
    price_total = fields.Float("Total inc Tax", digits="Account")
    effective_tax_rate = fields.Float("Effective Tax Rate", readonly=True)
    price_calculation_id = fields.Many2one("price.recalculation")

    def _update_pricing(self, as_at_date, pricelist):
        self.price_unit = pricelist._get_product_price(
            self.product_id,
            self.qty,
            date=as_at_date,
        )
        # self.price_subtotal = self.price_unit * self.qty
        # self.price_total = self.price_subtotal * (1 + self.effective_tax_rate)

    @api.depends("price_unit")
    def _compute_price_unit(self):
        for price_line in self:
            price_line._calculate_totals(price_unit=self.price_unit)

    @api.depends("price_total")
    def _compute_price_and_total(self):
        price_subtotal = self.price_total / (1 + self.effective_tax_rate)
        self._calculate_totals(price_subtotal=price_subtotal)

    @api.depends("price_subtotal")
    def _compute_price_subtotal(self):
        for price_line in self:
            price_line._calculate_totals(price_subtotal=price_line.price_subtotal)

    def _calculate_totals(self, price_unit=False, price_subtotal=False):
        price_prec = self.price_calculation_id.precision or self.env["decimal.precision"].precision_get("Product Price")
        total_prec = self.env["decimal.precision"].precision_get("Account")
        if price_subtotal:
            self.price_unit = float_round(
                price_subtotal / (self.qty or 1.0),
                self._context.get("precision", price_prec),
            )
        self.price_unit = price_unit
        self.price_subtotal = float_round(self.price_unit * self.qty, total_prec)
        self.price_total = float_round(self.price_subtotal * (1 + self.effective_tax_rate), total_prec)



