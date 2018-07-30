# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        related="procurement_group_id.sale_id",
        store=True,
    )
    partner_id = fields.Many2one(
        related="sale_id.partner_id", string="Customer", store=True
    )
