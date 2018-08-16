# Copyright 2018 Graeme Gellatly.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import api, models


class CustomerActivityStatement(models.AbstractModel):
    """Model of Customer Activity Statement"""

    _inherit = "report.customer_activity_statement.statement"

    def _get_bucket_dates(self, date_end):
        if self._context.get("aging_type", "") == "months":
            res = {}
            d = date_end
            for k in (
                "date_end",
                "minus_30",
                "minus_60",
                "minus_90",
                "minus_120",
            ):
                res[k] = d
                d = d.replace(day=1) - timedelta(days=1)
            return res
        else:
            return super()._get_bucket_dates(date_end)

    @api.multi
    def get_report_values(self, docids, data):
        aging_type = data["aging_type"]
        res = super(
            CustomerActivityStatement, self.with_context(aging_type=aging_type)
        ).get_report_values(docids, data)
        res["aging_type"] = aging_type
        return res
