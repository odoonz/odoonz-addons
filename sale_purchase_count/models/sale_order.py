# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    purchase_count = fields.Integer(string='Purchase Orders',
                                    compute='_compute_purchase_ids')

    @api.multi
    def _compute_purchase_ids(self):
        Purchase = self.env['purchase.order']
        for order in self:
            order.purchase_count = len(
                Purchase.search([('origin', 'ilike', order.name)]))

    @api.multi
    def action_view_purchase(self):
        """
        This function returns an action that display existing purchase orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one purchase order to show.
        """
        self.ensure_one()
        Purchase = self.env['purchase.order']
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        purchases = Purchase.search([('origin', 'ilike', self.name)])
        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        elif purchases:
            action['views'] = [(self.env.ref(
                'purchase.purchase_order_form').id, 'form')]
            action['res_id'] = purchases.id
        return action
