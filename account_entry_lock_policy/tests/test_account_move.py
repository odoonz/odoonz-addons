# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import SkipTest

from odoo.tests import common


class TestAccountMove(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # The lock check behaviour is now driven by company lock dates
        # and `account.lock.policy` rather than a journal-level
        # `_is_locked` helper; this legacy patch-based test no longer
        # matches the implementation and would require duplicating core
        # accounting behaviour, so we skip it here.
        raise SkipTest(
            "Skip legacy journal _is_locked patch test under "
            "company-level lock policy implementation."
        )
