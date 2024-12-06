import logging
import unittest.mock as mock

from odoo.tests import tagged

from odoo.addons.sale.tests.test_sale_order import TestSaleOrder

_logger = logging.getLogger(__name__)
WIZARD = (
    "odoo.addons.price_recalculation.wizards.price_recalculation.PriceRecalculation"
)


@tagged("post-install", "-at-install")
class TestPriceCalculation(TestSaleOrder):
    def setUp(self):
        """Initial Setup"""
        super().setUp()

    def test_defaults(self):
        with mock.patch("%s._get_lines" % WIZARD) as get_lines:
            get_lines.return_value = []
            flds = (
                self.env["price.recalculation"]
                .with_context(
                    active_ids=[self.sale_order.id], active_model="sale.order"
                )
                .default_get(["name", "partner_id", "line_ids", "as_at_date"])
            )
        self.assertEqual(flds["name"], self.sale_order.id)
        self.assertEqual(flds["partner_id"], self.sale_order.partner_id.id)
        self.assertEqual(flds["as_at_date"], self.sale_order.date_order)
