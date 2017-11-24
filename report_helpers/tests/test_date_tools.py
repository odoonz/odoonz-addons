# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.fields import Date
from odoo.fields import Datetime


class TestDateTools(TransactionCase):

    def test_adjust_date(self):
        date_string = Date.today()
        adj_string = Date.adjust_date(date_string, weeks=1, days=3)
        adj_string = Date.adjust_date(adj_string, weeks=-1, days=-3)
        self.assertEqual(adj_string, date_string)

    def test_adjust_datetime(self):
        dt_string = Datetime.now()
        adj_string = Datetime.adjust_datetime(dt_string, weeks=1, days=3)
        adj_string = Datetime.adjust_datetime(adj_string, weeks=-1, days=-3)
        self.assertEqual(adj_string, dt_string)
