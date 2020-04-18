# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def create(self, vals):
        """
        Assuming there is no hook to prevent using context
        :return:
        """
        force_date = self.env.context.get("force_period_date", False)
        if "date" not in vals and force_date:
            vals.update({"date": force_date})
        return super().create(vals)
