# Copyright 2019 Graeme Gelatly <graeme@o4sb.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
        bom,
    ):
        res = super()._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin, values, bom
        )
        res.update(
            {
                "procurement_group_id": values.get(
                    "group_id", env["procurement.group"]
                ).id
            }
        )
        return res
