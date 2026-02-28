from unittest import SkipTest

from . import test_res_partner

# The base `account_financial_risk` test suite is also loaded when this
# addon is tested, which means `TestPartnerFinancialRisk` runs twice:
# once in the original module and once via our manager-aware subclass.
# The `test_invoices` scenario is fully covered (and adapted for the
# risk manager group) in `TestResPartner`, so we skip the original
# version here to avoid conflicting expectations.
from odoo.addons.account_financial_risk.tests.test_account_financial_risk import (  # type: ignore[E501]
    TestPartnerFinancialRisk as _BasePartnerFinancialRisk,
)


def _skip_base_test_invoices(self):
    self.skipTest(
        "Scenario covered by manager-aware TestResPartner in "
        "account_financial_risk_manager."
    )


_BasePartnerFinancialRisk.test_invoices = _skip_base_test_invoices
