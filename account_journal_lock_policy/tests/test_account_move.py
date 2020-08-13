# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.exceptions import UserError
from odoo.tests import common

module = (
    "odoo.addons.account_journal_lock_policy.models." "account_journal.AccountJournal"
)


class TestAccountMove(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_get_lock_date_fail(self):
        with mock.patch("%s._is_locked" % module, autospec=True) as lock:
            with self.assertRaises(UserError):
                lock.return_value = True
                journal = self.env["account.journal"].search(
                    [("type", "=", "bank")], limit=1
                )
                company_id = self.env["res.users"].browse(self.env.uid).company_id.id

                move = self.env["account.move"].create(
                    {
                        "name": "/",
                        "ref": "2011010",
                        "journal_id": journal.id,
                        "state": "draft",
                        "company_id": company_id,
                    }
                )
                move._check_fiscalyear_lock_date()
