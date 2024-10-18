# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from builtins import range

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class AccountLockPolicy(models.Model):

    _name = "account.lock.policy"

    lock_date_field = fields.Selection(
        [
            ("sale_lock_date", "Sales"),
            ("purchase_lock_date", "Purchases"),
            ("tax_lock_date", "Tax"),
            ("fiscalyear_lock_date", "Global"),
        ],
        string="Lock Date Target",
    )

    days = fields.Integer()
    day_type = fields.Selection([("weekday", "working days"), ("day", "days")])
    months = fields.Integer()
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    def button_update_lock_date(self):
        companies = self.company_id or self.env["res.company"].search([])
        companies.check_access("write")
        for lock_policy in self:
            lock_policy._update_lock_dates()

    def _cron_update_lock_dates(self):
        for lock_policy in self.search([]):
            lock_policy._update_lock_dates()

    def _update_lock_dates(self):
        companies = self.company_id or self.env["res.company"].search([])
        for company in companies:
            lock_date = self.with_context(
                tz=company.partner_id.tz or self.env.context.get("tz")
            )._calculate_lock_date()
            if company._lock_can_be_set(lock_date, self.lock_date_field):
                company[self.lock_date_field] = lock_date

    def _calculate_lock_date(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        earliest_date = today - relativedelta(day=31, months=self.months)
        if self._over_days_limit(today):
            earliest_date = earliest_date - relativedelta(months=1)
        return earliest_date

    def _over_days_limit(self, date_to):
        self.ensure_one()
        days = self.days
        if self.day_type == "weekday":
            date_from = date_to - relativedelta(months=1, day=31)
            all_days = (
                date_from + relativedelta(days=x + 1) for x in range(date_to.day)
            )
            count = sum(1 for day in all_days if day.weekday() < 5)
            days = count
        return date_to.day > days


class ResCompany(models.Model):
    _inherit = "res.company"

    def _lock_can_be_set(self, lock_date, lock_date_field):
        self.ensure_one()
        return not self[lock_date_field] or self[lock_date_field] < lock_date
