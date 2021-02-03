# Copyright 2021 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account_financial_risk.tests.test_account_financial_risk import (
    TestPartnerFinancialRisk,
)


class TestResPartner(TestPartnerFinancialRisk):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref(
            "account_financial_risk_manager.group_risk_manager"
        )
