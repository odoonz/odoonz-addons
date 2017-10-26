# -*- coding: utf-8 -*-
# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    def name_get(self):
        res = super(StockProductionLot, self).name_get()
        if self.env.context.get('show_qty'):
            res = self.browse([r[0] for r in res]).mapped(
                lambda r: (r.id, r.name + '(%.3f) ' % r.product_qty))
        return res
