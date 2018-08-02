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
        self.partner = self.env.ref("base.res_partner_1")
        self.today = datetime.strptime(
            fields.Date.context_today(self.partner), DEFAULT_SERVER_DATE_FORMAT
        )
        self.days = 7

    def test_get_lock_date_normal(self):
        self.partner.write({"enforce_cutoff": False})
        self.assertEqual(
            self.partner._get_lock_date("2018-12-1972"), "2018-12-1972"
        )

    def test_get_lock_date_weekdays(self):
        self.partner.write(
            {
                "enforce_cutoff": True,
                "days": self.days,
                "day_type": "weekday",
                "cutoff_type": "date",
            }
        )
        tdate1 = fields.Date.to_string(
            self.today - relativedelta(days=self.days + 1)
        )
        tdate2 = fields.Date.to_string(self.today - relativedelta(days=4))

        self.assertEqual(self.partner._get_lock_date(tdate1), tdate1)
        self.assertEqual(self.partner._get_lock_date(tdate2), tdate2)

    def test_get_lock_date_days(self):
        self.partner.write(
            {
                "enforce_cutoff": True,
                "days": self.days,
                "day_type": "day",
                "cutoff_type": "date",
            }
        )
        tdate1 = fields.Date.to_string(
            self.today - relativedelta(days=self.days)
        )
        tdate2 = fields.Date.to_string(
            self.today - relativedelta(days=self.days - 1)
        )
        today = fields.Date.to_string(self.today)

        self.assertEqual(self.partner._get_lock_date(tdate1), today)
        self.assertEqual(self.partner._get_lock_date(tdate2), tdate2)

    def test_get_lock_date_eom(self):
        self.partner.write(
            {
                "enforce_cutoff": True,
                "days": self.days,
                "day_type": "day",
                "cutoff_type": "eom",
            }
        )
        # In middle of previous month, depends on rule.
        tdate1 = fields.Date.to_string(
            self.today + relativedelta(months=-1, day=14)
        )
        # In future, keeps date
        tdate2 = fields.Date.to_string(
            self.today + relativedelta(months=1, days=self.days)
        )
        # 2 months old, 1st of current month
        tdate3 = fields.Date.to_string(
            self.today + relativedelta(months=-2)
        )
        # In current month keeps same date
        tdate4 = fields.Date.to_string(
            self.today + relativedelta(day=1)
        )
        first_of_month = fields.Date.to_string(self.today + relativedelta(day=1))
        # Depending on what day today is the behaviour in test will differ
        if self.today.day >= self.days:
            expected = first_of_month
        else:
            expected = tdate1
        self.assertEqual(self.partner._get_lock_date(tdate1), expected)
        self.assertEqual(self.partner._get_lock_date(tdate2), tdate2)
        self.assertEqual(self.partner._get_lock_date(tdate3), first_of_month)
        self.assertEqual(self.partner._get_lock_date(tdate4), tdate4)


    def test_commercial_fields(self):
        comm_fields = self.env["res.partner"]._commercial_fields()
        self.assertIn("enforce_cutoff", comm_fields)
        self.assertIn("days", comm_fields)
        self.assertIn("day_type", comm_fields)
        self.assertIn("cutoff_type", comm_fields)
