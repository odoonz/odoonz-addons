# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.workorder"

    sale_id = fields.Many2one(related="production_id.sale_id", store=True)
    partner_id = fields.Many2one(related="production_id.partner_id", store=True)
