# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "reference_ids.sale_ids",
        "sale_line_id",
        "sale_line_id.order_id",
    )
    def _compute_sale_order(self):
        for prod in self:
            prod.sale_id = prod.reference_ids.sale_ids | prod.sale_line_id.order_id

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        readonly=True,
        compute="_compute_sale_order",
        store=True,
    )

    partner_id = fields.Many2one(
        related="sale_id.partner_id", string="Customer", store=True
    )
