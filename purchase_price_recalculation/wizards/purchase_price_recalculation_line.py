# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchasePriceRecalculationLine(models.TransientModel):
    _inherit = "price.recalculation.line"
    _name = "purchase.price.recalculation.line"
    _description = "Purchase Price Recalculation Line"

    name = fields.Many2one(comodel_name="purchase.order.line", readonly=True)
    price_recalculation_id = fields.Many2one(
        comodel_name="purchase.price.recalculation", string="Price Recalculation"
    )
