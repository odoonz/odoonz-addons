# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class PriceRecalculationLine(models.AbstractModel):
    _name = "price.recalculation.line"
    _description = "Price Recalculation Line"

    price_calculation_id = fields.Many2one("price.recalculation")
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    qty = fields.Float(digits="Product Unit of Measure", readonly=True)
    price_unit = fields.Float("Unit Price", required=True, digits="Product Price")
    discount = fields.Float("Discount (%)", digits="Discount")
    discount_factor = fields.Float(
        "Discount factor)",
        digits="Discount",
        compute="_compute_discount_factor",
    )
    price_subtotal = fields.Float(
        "Total ex Tax",
        digits="Account",
        compute="_compute_price_subtotal",
        readonly=False,
    )
    price_total = fields.Float(
        "Total inc Tax",
        digits="Account",
        compute="_compute_price_total",
        readonly=False,
    )
    effective_tax_rate = fields.Float(readonly=True)

    def _compute_discount_factor(self):
        for line in self:
            line.discount_factor = (100.0 - line.discount) / 100.0

    @api.depends("qty", "price_unit", "discount")
    def _compute_price_subtotal(self):
        """Determine line components from unit price"""
        for line in self:
            line._compute_line(price_unit=line.price_unit)

    @api.depends("price_subtotal")
    def _compute_price_total(self):
        """Determine line components from subtotal"""
        for line in self:
            line._compute_line(price_subtotal=line.price_subtotal)

    @api.onchange("price_total")
    def _onchange_price_total(self):
        """Determine line components from total

        NB when triggered again by _compute_line() this is a no-op
        as the total was just determined and nothing else changed.
        """
        self._compute_line(price_total=self.price_total)

    def _compute_line(self, price_total=False, price_subtotal=False, price_unit=False):
        """Compute line components from each other

        Whichever component was set is used to determine the other values
        (see @api.depends() on the compute methods and _onchange_price_total() above)

        NB A subtotal may be set but not possible because of the unit price precision.
        It will be re-determined from the rounded unit price to the closest value
        (the discount is never changed).
        """
        precision_total = self.env["decimal.precision"].precision_get("Account")
        if price_total is not False:
            # Total was set: Calculate subtotal from total
            price_subtotal = float_round(
                self.price_total / (1 + self.effective_tax_rate),
                precision_total,
            )
        if price_subtotal is not False:
            # Subtotal was set or calculated just now: Calculate unit price from subtotal
            price_unit = price_subtotal / (self.qty or 1.0) / self.discount_factor
        if price_unit is not False:
            # Unit price was set or calculated just now: Round for new subtotal
            precision_price = self.price_calculation_id.precision or self.env[
                "decimal.precision"
            ].precision_get("Product Price")
            self.price_unit = float_round(price_unit, precision_price)
        # Calculate subtotal again
        # (possibly rounded from unit price rounding from originally set value)
        self.price_subtotal = float_round(
            self.price_unit * self.qty * self.discount_factor, precision_total
        )
        # Calculate total again
        # (will trigger no-op recalculation in onchange() but needed for manual user changes)
        self.price_total = float_round(
            self.price_subtotal * (1 + self.effective_tax_rate), precision_total
        )
