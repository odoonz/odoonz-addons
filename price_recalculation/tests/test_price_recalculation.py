import logging
import unittest.mock as mock

from odoo.addons.sale.tests.test_sale_order import TestSaleOrder

_logger = logging.Logger(__name__)

wizard = (
    "odoo.addons.price_recalculation.wizards." "price_recalculation.PriceRecalculation"
)


class TestPriceCalculation(TestSaleOrder):
    def setUp(self):
        """Initial Setup"""
        super().setUp()

    def test_defaults(self):
        with mock.patch("%s._get_lines" % wizard) as get_lines:
            get_lines.return_value = []
            flds = (
                self.env["price.recalculation"]
                .with_context(
                    active_ids=[self.sale_order.id], active_model="sale.order"
                )
                .default_get(["name", "partner_id", "line_ids", "date_order"])
            )
        self.assertEqual(flds["name"], self.sale_order.id)
        self.assertEqual(flds["partner_id"], self.sale_order.partner_id.id)
        self.assertEqual(flds["date_order"], self.sale_order.date_order)
