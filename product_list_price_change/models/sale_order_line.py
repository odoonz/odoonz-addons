# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_price_context(self):
        """Make the pricelist-based price computation partner-aware.

        Without this, ``product.product._compute_product_lst_price`` /
        ``_compute_product_price_extra`` (see ``product_product.py`` in this
        module) never receive ``partner_id`` in context during
        ``_get_pricelist_price``/``_get_pricelist_price_before_discount``, so
        a customer-specific implementation delay on a price change never
        actually affects the price used on a quotation/sale order line - it
        only ever applied when something else happened to pass
        ``partner_id`` in context (e.g. product selector widgets), which is
        an implementation detail, not the source of truth for order pricing.
        """
        res = super()._get_product_price_context()
        partner = self.order_id.partner_id
        if partner:
            res["partner_id"] = partner.id
        return res
