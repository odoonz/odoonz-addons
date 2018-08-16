# Copyright 2018 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from odoo import fields, api, models


class CustomerActivityStatementWizard(models.TransientModel):

    _inherit = "customer.activity.statement.wizard"

    @api.model
    def _default_date_start(self):
        return fields.Date.to_string(
            (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        )

    @api.model
    def _default_date_end(self):
        return fields.Date.to_string(
            date.today().replace(day=1) - timedelta(days=1)
        )

    date_start = fields.Date(default=_default_date_start)
    date_end = fields.Date(default=_default_date_end)

    aging_type = fields.Selection(
        [("days", "Age by Days"), ("months", "Age by Months")],
        string="Aging Method",
        default="months",
        required=True,
    )

    def _prepare_activity_statement(self):
        result = super()._prepare_activity_statement()
        result["aging_type"] = self.aging_type
        return result
