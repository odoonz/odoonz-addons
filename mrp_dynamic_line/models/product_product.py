# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_used_in_bom_count(self):
        for product in self:
            product.used_in_bom_count = self.env["mrp.bom"].search_count(
                [("bom_line_ids.product_tmpl_id", "=", product.product_tmpl_id.id)]
            )

    def action_used_in_bom(self):
        self.ensure_one()
        action = self.env.ref("mrp.mrp_bom_form_action").read()[0]
        action["domain"] = [
            ("bom_line_ids.product_tmpl_id", "=", self.product_tmpl_id.id)
        ]
        return action

    def _compute_bom_price_by_type(
        self, bom, price="standard_price", labour="costs_hour"
    ):
        self.ensure_one()
        if not bom:
            return 0
        boms, bom_lines = bom.explode(self, 1)
        total = 0
        for line, explode_details in bom_lines:
            line_qty = explode_details["qty"]
            product = explode_details["product"]
            product = line.product_id
            total += (
                line.product_id.uom_id._compute_price(
                    product[price], line.product_uom_id
                )
                * line_qty
            )
            _logger.debug(
                f"Bom: {bom.product_tmpl_id.name}, Qty: {line_qty}, "
                f"Price: {product[price]} {price}, Total: {total}"
            )
        for opt in bom.operation_ids:
            duration_expected = (
                # We remove setup and tear down time as they apply across multiple units
                opt.time_cycle
            )
            total += (duration_expected / 60) * opt.workcenter_id[labour]
        return bom.product_uom_id._compute_price(total / bom.product_qty, self.uom_id)

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        return self._compute_bom_price_by_type(bom)
