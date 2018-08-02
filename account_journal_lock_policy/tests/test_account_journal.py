# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestResPartner(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        self.today = datetime.strptime(
            fields.Date.context_today(self.journal), DEFAULT_SERVER_DATE_FORMAT
        )
        self.days = 7

    def test_is_locked_normal(self):
        self.journal.write({"enforce_lock": False})
        self.assertFalse(self.journal._is_locked("2018-12-1972"))

    def test_is_locked_weekdays(self):
        # Journal Transactions can be no older than 1mo 7 weekdays
        self.journal.write(
            {
                "enforce_lock": True,
                "days": self.days,
                "months": 1,
                "day_type": "weekday",
                "cutoff_type": "date",
            }
        )
        tdate1 = fields.Date.to_string(
            self.today + relativedelta(days=self.days + 1)
        )
        tdate2 = fields.Date.to_string(
            self.today - relativedelta(months=1, days=7)
        )

        self.assertFalse(self.journal._is_locked(tdate1))
        self.assertFalse(self.journal._is_locked(tdate2))

    def test_is_locked_days(self):
        self.journal.write(
            {
                "enforce_lock": True,
                "days": self.days,
                "months": 1,
                "day_type": "day",
                "cutoff_type": "date",
            }
        )
        tdate1 = fields.Date.to_string(
            self.today + relativedelta(days=self.days + 1)
        )
        tdate2 = fields.Date.to_string(
            self.today - relativedelta(months=1, days=7)
        )

        self.assertFalse(self.journal._is_locked(tdate1))

        self.assertTrue(self.journal._is_locked(tdate2))

    def test_is_locked_eom(self):
        # Note test with zero days here or else tests will fail
        # until x days into month
        self.journal.write(
            {
                "enforce_lock": True,
                "days": 0,
                "months": 1,
                "day_type": "day",
                "cutoff_type": "eom",
            }
        )
        tdate1 = fields.Date.to_string(
            self.today + relativedelta(months=-1, day=1)
        )
        tdate2 = fields.Date.to_string(
            self.today + relativedelta(months=1, days=self.days)
        )
        tdate3 = fields.Date.to_string(self.today + relativedelta(months=-2))

        self.assertFalse(self.journal._is_locked(tdate1))
        self.assertFalse(self.journal._is_locked(tdate2))
        self.assertTrue(self.journal._is_locked(tdate3))
