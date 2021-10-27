# Copyright 2021 O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def operating_unit_default_get(self, uid2=False):
        default_ou = super().operating_unit_default_get(uid2=uid2)
        if not uid2:
            uid2 = self._uid
        user = self.env["res.users"].browse(uid2)
        company_id = self.env.context.get("force_company")
        if not company_id:
            try:
                company_id = self.env.context["allowed_company_ids"][0]
            except (KeyError, IndexError):
                company_id = user.company_id.id
        if default_ou.company_id.id != company_id:
            default_ou = user.operating_unit_ids.filtered(
                lambda s: s.company_id.id == company_id
            )[:1]
        return default_ou
