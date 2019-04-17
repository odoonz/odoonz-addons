# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _get_fifo_candidates_in_move_with_company(self, move_company_id=False):
        """ Find IN moves that can be used to value OUT moves. Prioritze actual
        lot records over general records for tracked products.
        """
        self.ensure_one()
        candidates = self.env["stock.move"]
        domain = [
            ("product_id", "=", self.id),
            ("remaining_qty", ">", 0.0),
        ] + self.env["stock.move"]._get_in_base_domain(company_id=move_company_id)
        if self.env.context.get("lots"):
            domain_lots = domain[:]
            self._cr.execute(
                """SELECT DISTINCT move_id FROM stock_move_line WHERE lot_id IN %s""",
                (tuple(self.env.context["lots"].keys()),),
            )
            move_ids = [m[0] for m in self._cr.fetchall() if m]
            if move_ids:
                domain_lots.append(("id", "in", move_ids))
                candidates |= self.env["stock.move"].search(
                    domain_lots, order="date, id"
                )
                if candidates:
                    domain.append(("id", "not in", candidates.ids))
        candidates |= self.env["stock.move"].search(domain, order="date, id")
        return candidates
