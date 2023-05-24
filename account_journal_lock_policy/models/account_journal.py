# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from builtins import range

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    enforce_lock = fields.Selection([("policy", "Lock Policy"), ("fixed", "Fixed Date"), ("none", "No Lock")], default="none")
    days = fields.Integer()
    day_type = fields.Selection([("weekday", "working days"), ("day", "days")])
    months = fields.Integer()
    cutoff_type = fields.Selection(
        [("date", "transaction date"), ("eom", "end of month following transaction")],
    )
    cutoff_date = fields.Date()

    def _is_locked(self, transaction_date):
        self.ensure_one()
        if self.enforce_lock == "none":
            return False
        today = fields.Date.context_today(self)
        if not transaction_date:
            transaction_date = today

        if transaction_date >= today:
            return False
        if self.enforce_lock == "fixed":
            return not(transaction_date >= self.cutoff_date)

        if self.cutoff_type == "eom":
            transaction_date += relativedelta(day=31)
            if transaction_date >= today:
                return False
        if self.months:
            transaction_date += relativedelta(months=self.months)
        if self.days:
            weekdays = list(range(5 if self.day_type == "weekday" else 7))
            transaction_date = rrule(
                DAILY, count=self.days, byweekday=weekdays, dtstart=transaction_date
            )[-1].date()

        if transaction_date < today:
            return True
        return False
