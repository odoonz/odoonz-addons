# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        related="production_id.sale_id", string="Sale order", readonly=True, store=True
    )

    partner_id = fields.Many2one(
        related="sale_id.partner_id", string="Customer", store=True
    )
