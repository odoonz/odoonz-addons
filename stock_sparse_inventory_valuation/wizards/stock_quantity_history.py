# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuantityHistory(models.TransientModel):

    _inherit = "stock.quantity.history"

    def open_table(self):
        if not self.env.context.get("valuation"):
            return super(StockQuantityHistory, self).open_table()
        action = super(StockQuantityHistory, self).open_table()
        context = dict(company_owned=True, owner_id=False)
        if self.compute_at_date:
            context.update(to_date=self.date)
        products = (
            self.env["stock.move"]
            .search([("date", "<=", self.date)])
            .mapped("product_id")
            .with_context(**context)
            .filtered(lambda s: s.type == "product" and s.qty_available)
        )
        if products:
            action["domain"] = "['id', 'in', %s]" % products.ids
        return action
