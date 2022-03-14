# Copyright 2022 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    enforce_limit_sale = fields.Boolean(
        related="company_id.enforce_limit_sale", readonly=False
    )
    allowed_min_sale = fields.Float(
        related="company_id.allowed_min_sale", readonly=False
    )
