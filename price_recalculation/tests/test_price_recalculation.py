import logging
import unittest.mock as mock

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)
WIZARD = (
    "odoo.addons.price_recalculation.wizards.price_recalculation.PriceRecalculation"
)


@tagged("post_install", "-at_install")
class TestPriceCalculation(TransactionCase):
    """Minimal test setup for price recalculation wizard tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            su=True
        )  # Use sudo to bypass master_data_security if installed
        cls.company = cls.env.company

        # Create partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_id": False,
            }
        )

        # Create products
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 20.0,
            }
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Test Service Product",
                "type": "service",
                "list_price": 50.0,
            }
        )

        # Create sale order (needed for test_defaults)
        cls.empty_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.service_product.id,
                            "product_uom_qty": 12.5,
                        }
                    ),
                ],
            }
        )

    def test_defaults(self):
        with mock.patch(f"{WIZARD}._get_lines") as get_lines:
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
