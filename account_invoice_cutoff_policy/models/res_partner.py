# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    enforce_cutoff = fields.Boolean(default=False)
    days = fields.Integer()
    day_type = fields.Selection([("weekday", "working days"), ("day", "days")])
    cutoff_type = fields.Selection(
        [("date", "transaction date"), ("eom", "end of month following transaction")]
    )

    def _get_new_invoice_date(self, today):
        if self.cutoff_type == "eom":
            return today + relativedelta(day=1)
        else:
            return today

    def _get_lock_date(self, invoice_date):
        dates = [invoice_date]
        for partner in self:
            if not partner.enforce_cutoff:
                continue
            today = fields.Date.context_today(partner)
            transaction_date = invoice_date
            if transaction_date >= today:
                continue
            if partner.cutoff_type == "eom":
                eom = transaction_date + relativedelta(day=31)
                if eom >= today:
                    continue
                # Set to last day of month so we know if inside cutoff window
                transaction_date = eom
            if partner.days:
                weekdays = list(range(5 if partner.day_type == "weekday" else 7))
                transaction_date = rrule(
                    DAILY,
                    count=partner.days,
                    byweekday=weekdays,
                    dtstart=transaction_date,
                )[-1].date()
            if transaction_date < today:
                dates.append(partner._get_new_invoice_date(today))
        return max(dates)

    @api.model
    def _commercial_fields(self):
        """Returns the list of fields that are managed by the commercial entity
        to which a partner belongs. These fields are meant to be hidden on
        partners that aren't `commercial entities` themselves, and will be
        delegated to the parent `commercial entity`. The list is meant to be
        extended by inheriting classes."""
        return super()._commercial_fields() + [
            "enforce_cutoff",
            "days",
            "day_type",
            "cutoff_type",
        ]
