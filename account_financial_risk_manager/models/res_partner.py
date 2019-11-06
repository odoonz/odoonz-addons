# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_risk_allow_edit(self):
        is_editable = self.env.user.has_group("account_financial_risk_manager.group_risk_manager")
        for partner in self.filtered("customer"):
            partner.risk_allow_edit = is_editable
