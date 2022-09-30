# Copyright 2022 O4SB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    intracompany_user_id = fields.Many2one(
        "res.users",
        string="Create as",
        help="Responsible user for actions that need to be restricted to just this company.",
    )
