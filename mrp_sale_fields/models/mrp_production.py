# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    @api.depends(
        "procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id"
    )
    def _compute_sale_order(self):
        for production in self:
            production.sale_id = (
                production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
            )

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
