# Copyright 2022 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    enforce_limit_sale = fields.Boolean(string="Sale must have limit")
    allowed_min_sale = fields.Float(default="500.0")
