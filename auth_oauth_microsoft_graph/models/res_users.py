# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _generate_signup_values(self, provider, validation, params):
        values = super()._generate_signup_values(provider, validation, params)
        values["email"] = validation.get("userPrincipalName", values["email"])
        values["login"] = values["email"]
        values["name"] = validation.get("displayName", values["email"])
        return values
