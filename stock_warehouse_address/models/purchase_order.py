# Copyright 2017 Graeme Gellatly
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_sale_order_data(
            self, name, partner, company, direct_delivery_address):
        """Used in intercompany rules"""
        sale_order_vals = super(PurchaseOrder, self)._prepare_sale_order_data(
            name, partner, company, direct_delivery_address)
        if not direct_delivery_address:
            warehouse = self.warehouse
            sale_order_vals['partner_shipping_id'] = warehouse.partner_id.id
            sale_order_vals['partner_id'] = warehouse.postal_address_id.id
        return sale_order_vals
