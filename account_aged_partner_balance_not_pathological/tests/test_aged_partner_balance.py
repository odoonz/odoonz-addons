# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import inspect

from odoo.tests.common import TransactionCase

from odoo.addons.account.report.account_aged_partner_balance import (
    ReportAgedPartnerBalance as upstream,
)

VALID_HASHES = ["3b3162b85fe09efa7caa1a2883d54e38"]


class TestAgedPartnerBalance(TransactionCase):
    def setUp(self):
        super(TestAgedPartnerBalance, self).setUp()

    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._get_partner_move_lines).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_HASHES)
