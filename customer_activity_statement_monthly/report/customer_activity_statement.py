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
        if not data:
            wiz = self.env["customer.activity.statement.wizard"].with_context(
                active_ids=docids, model="res.partner"
            )
            data = wiz.create({})._prepare_activity_statement()
        aging_type = data["aging_type"]
        res = super(
            CustomerActivityStatement, self.with_context(aging_type=aging_type)
        ).get_report_values(docids, data)
        res["aging_type"] = aging_type

        partner_ids = res["doc_ids"] # To keep order
        if data["filter_non_due_partners"] and len(res["doc_ids"]) > 1:
            partner_ids = [k for k, v in res["Lines"].items() if v]
        if data["filter_negative_balances"]:
            # Because amounts are double nested we need to
            # collapse first e.g
            # {<partner_id (k)>: {<currency>: <amount>} {}...}
            max_amount = dict(
                [
                    (k, max([v2 for v2 in list(v.values())] + [0.0]))
                    for k, v in res["Amount_Due"].items()
                ]
            )
            partner_ids = [
                k
                for k, v in max_amount.items()
                if v > 0.0 and k in partner_ids
            ]
        res["doc_ids"] = [x for x in res["doc_ids"] if x in partner_ids]
        res["docs"] = self.env["res.partner"].browse(res["doc_ids"])
        return res
