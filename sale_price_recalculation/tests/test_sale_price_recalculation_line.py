# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from hypothesis import HealthCheck, settings

from odoo.tests import tagged

from odoo.addons.price_recalculation.tests.test_price_recalculation_line import (
    TestPriceRecalculationLine,
)


@tagged("post_install", "-at_install")
@settings(suppress_health_check=[HealthCheck.differing_executors])
class TestSalePriceRecalculationLine(TestPriceRecalculationLine):
    def setUp(self):
        """Set model to enable base tests (skipped for the AbstractModel)"""
        super().setUp()
        self.model = self.env["sale.price.recalculation.line"]
