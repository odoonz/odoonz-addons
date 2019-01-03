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
        product_ids = [
            item["product_id"][0]
            for item in self.env["stock.move"].read_group(
                [("date", "<=", self.date), ("state", "=", "done")],
                ["product_id"],
                ["product_id"],
                orderby="id",
            )
        ]
        if product_ids:
            action["domain"] = "[('id', 'in', %s)]" % product_ids
        return action
