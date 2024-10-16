# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("is_landed_costs_line")
    def _onchange_is_landed_costs_line(self):
        res = super()._onchange_is_landed_costs_line()
        if self.is_landed_costs_line:
            self.move_id.anglo_saxon_financial = False
        return res
