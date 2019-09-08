# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductPriceChangeLine(models.Model):

    _name = "product.price.change.line"
    _description = "Product Price Change Line"
    _rec_name = "product_tmpl_id"
    _order = "effective_date desc, id"

    product_tmpl_id = fields.Many2one(
        string="Product",
        comodel_name="product.template",
        required=True,
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )
    price_change_id = fields.Many2one(
        string="Price Change",
        comodel_name="product.price.change",
        required=True,
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )
    list_price = fields.Float(
        "Sales Price",
        required=True,
        digits=dp.get_precision("Product Price"),
        help="Price at which the product is sold to customers.",
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )

    state = fields.Selection(related="price_change_id.state", store=True)
    effective_date = fields.Date(related="price_change_id.effective_date", store=True)

    percent_change = fields.Float(string="% Change")

    @api.onchange("product_tmpl_id")
    def _change_product_tmpl_id(self):
        for record in self:
            if not record.product_tmpl_id:
                return
            record.list_price = round(
                record.product_tmpl_id.list_price
                * ((100.0 + record.percent_change) / 100.0),
                2,
            )

    @api.onchange("percent_change")
    def _change_percent(self):
        for record in self:
            record.list_price = round(
                record.product_tmpl_id.list_price
                * ((100.0 + record.percent_change) / 100.0),
                2,
            )

    @api.onchange("list_price")
    def _change_list_price(self):
        for record in self:
            if record.product_tmpl_id and record.product_tmpl_id.list_price:
                record.percent_change = (
                    (record.list_price / record.product_tmpl_id.list_price) - 1
                ) * 100.0
