# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SalePriceRecalculationLine(models.TransientModel):
    _inherit = "price.recalculation.line"
    _name = "sale.price.recalculation.line"
    _description = "Sale Price Recalculation Line"

    name = fields.Many2one(comodel_name="sale.order.line", readonly=True)
    price_recalculation_id = fields.Many2one(
        comodel_name="sale.price.recalculation", string="Price Recalculation"
    )

    def _update_pricing(self, as_at_date, pricelist):
        """Set unit price from pricelist as per given date and current quantity"""
        self.price_unit = pricelist._get_product_price(
            self.product_id,
            self.qty,
            date=as_at_date,
        )
