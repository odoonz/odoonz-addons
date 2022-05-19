# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import ValidationError


class ProductConfigSession(models.Model):

    _inherit = "product.config.session"

    def get_cfg_price(self, value_ids=None, custom_vals=None):
        product_tmpl = self.product_tmpl_id
        if not product_tmpl.lst_price_from_bom:
            return super().get_cfg_price(value_ids=value_ids, custom_vals=custom_vals)
        try:
            variant = self.create_get_variant(
                value_ids=value_ids, custom_vals=custom_vals
            )
        except ValidationError:
            return 0.0
        order_id = self.env.context.get("default_order_id")
        if not order_id:
            return variant.lst_price
        order = self.env["sale.order"].browse(order_id)
        variant = variant.with_context(
            lang=order.partner_id.lang,
            partner=order.partner_id,
            date=order.date_order,
            pricelist=order.pricelist_id.id,
        )
        return variant.price
