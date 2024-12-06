# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tests import tagged

from odoo.addons.price_recalculation.tests.test_price_recalculation_line import (
    TestPriceRecalculationLine,
)

_logger = logging.Logger(__name__)


@tagged("post-install", "-at-install")
class TestSalePriceRecalculationLine(TestPriceRecalculationLine):
    def setUp(self):
        """Set model to enable base tests (skipped for AbstractModel)"""
        super().setUp()
        self.model = self.env["sale.price.recalculation.line"]
