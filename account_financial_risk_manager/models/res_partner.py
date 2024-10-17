# Copyright 2019- Graeme Gellatly <graeme@moahub.nz>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_risk_allow_edit(self):
        self.update(
            {
                "risk_allow_edit": self.env.user.has_group(
                    "account_financial_risk_manager.group_risk_manager"
                )
            }
        )
