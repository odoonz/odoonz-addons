# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    production_count = fields.Integer(
        string='Production Orders',
        compute='_compute_production_ids')

    @api.multi
    def _compute_production_ids(self):
        Production = self.env['mrp.production']
        for order in self:
            order.production_count = len(
                Production.search([('sale_id', '=', order.id)]))

    @api.multi
    def action_view_production(self):
        """
        This function returns an action that display existing production orders
        of given sales order ids.
        """
        self.ensure_one()
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('sale_id', '=', self.id)]
        return action
