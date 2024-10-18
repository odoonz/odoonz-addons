# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.exceptions import UserError
from odoo.tests import common


class TestAccountMove(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_get_lock_date_fail(self):
        journal = self.env["account.journal"].search([("type", "=", "bank")], limit=1)
        with mock.patch.object(type(journal), "_is_locked", return_value=True):
            with self.assertRaises(UserError):
                company_id = self.env["res.users"].browse(self.env.uid).company_id.id

                move = self.env["account.move"].create(
                    {
                        "name": "/",
                        "ref": "2011010",
                        "journal_id": journal.id,
                        "state": "posted",
                        "company_id": company_id,
                    }
                )
                move._check_fiscalyear_lock_date()
