# Copyright 2024 Graeme Gellatly
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import date

from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockValuationHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

        # Create accounts
        cls.stock_valuation_account = cls.env["account.account"].create(
            {
                "name": "Stock Valuation",
                "code": "STOCK.VAL",
                "account_type": "asset_current",
                "company_ids": [(6, 0, [cls.company.id])],
            }
        )

        # Create product category with valuation account
        cls.product_categ = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_stock_valuation_account_id": cls.stock_valuation_account.id,
                "property_cost_method": "average",
            }
        )

        # Create products
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.product_categ.id,
                "standard_price": 10.0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.product_categ.id,
                "standard_price": 20.0,
            }
        )

        # Get or create warehouse
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        if not cls.warehouse:
            cls.warehouse = cls.env["stock.warehouse"].create(
                {
                    "name": "Test Warehouse",
                    "code": "TEST",
                    "company_id": cls.company.id,
                }
            )

        # Get stock location
        cls.stock_location = cls.warehouse.lot_stock_id

        # Create quants with stock using inventory mode
        cls.quant1 = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product1.id,
                    "location_id": cls.stock_location.id,
                    "inventory_quantity": 10.0,
                }
            )
        )
        cls.quant1.action_apply_inventory()

        cls.quant2 = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product2.id,
                    "location_id": cls.stock_location.id,
                    "inventory_quantity": 5.0,
                }
            )
        )
        cls.quant2.action_apply_inventory()

        # Create inventory location for loss/gain accounts (for BS adjustment tests)
        cls.inventory_location = cls.env["stock.location"].search(
            [
                ("usage", "=", "inventory"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        if not cls.inventory_location:
            cls.inventory_location = cls.env["stock.location"].create(
                {
                    "name": "Inventory",
                    "usage": "inventory",
                    "company_id": cls.company.id,
                }
            )
            # Create loss/gain accounts if needed
            if not cls.inventory_location.valuation_in_account_id:
                loss_account = cls.env["account.account"].create(
                    {
                        "name": "Inventory Loss",
                        "code": "INV.LOSS",
                        "account_type": "expense",
                        "company_ids": [(6, 0, [cls.company.id])],
                    }
                )
                cls.inventory_location.valuation_in_account_id = loss_account
            if not cls.inventory_location.valuation_out_account_id:
                gain_account = cls.env["account.account"].create(
                    {
                        "name": "Inventory Gain",
                        "code": "INV.GAIN",
                        "account_type": "income_other",
                        "company_ids": [(6, 0, [cls.company.id])],
                    }
                )
                cls.inventory_location.valuation_out_account_id = gain_account

    def test_compute_name(self):
        """Test that name is computed from date."""
        with freeze_time("2024-01-15"):
            valuation = self.env["stock.valuation.historical"].create(
                {
                    "date": fields.Date.today(),
                    "company_id": self.company.id,
                    "product_id": self.product1.id,
                    "location_id": self.stock_location.id,
                    "warehouse_id": self.warehouse.id,
                    "quantity": 10.0,
                    "currency_id": self.currency.id,
                    "value": 100.0,
                    "valuation_account_id": self.stock_valuation_account.id,
                }
            )
            self.assertEqual(valuation.name, "15 Jan 2024")

    def test_compute_cost_price(self):
        """Test that cost_price is computed correctly."""
        valuation = self.env["stock.valuation.historical"].create(
            {
                "date": fields.Date.today(),
                "company_id": self.company.id,
                "product_id": self.product1.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "quantity": 10.0,
                "currency_id": self.currency.id,
                "value": 100.0,
                "valuation_account_id": self.stock_valuation_account.id,
            }
        )
        self.assertEqual(valuation.cost_price, 10.0)

    def test_compute_cost_price_zero_quantity(self):
        """Test that cost_price is 0 when quantity is 0."""
        valuation = self.env["stock.valuation.historical"].create(
            {
                "date": fields.Date.today(),
                "company_id": self.company.id,
                "product_id": self.product1.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "quantity": 0.0,
                "currency_id": self.currency.id,
                "value": 0.0,
                "valuation_account_id": self.stock_valuation_account.id,
            }
        )
        self.assertEqual(valuation.cost_price, 0.0)

    @freeze_time("2024-01-31")
    def test_run_month_end_valuation_last_day(self):
        """Test that valuation runs on last day of month."""
        result = self.env["stock.valuation.historical"]._run_month_end_valuation()
        self.assertTrue(result)

        # Check that valuations were created
        valuations = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 31)), ("company_id", "=", self.company.id)]
        )
        self.assertTrue(valuations)
        # Should have valuations for both products
        self.assertIn(self.product1, valuations.mapped("product_id"))
        self.assertIn(self.product2, valuations.mapped("product_id"))

    @freeze_time("2024-01-15")
    def test_run_month_end_valuation_not_last_day(self):
        """Test that valuation does not run when not last day of month."""
        result = self.env["stock.valuation.historical"]._run_month_end_valuation()
        self.assertFalse(result)

        # Check that no valuations were created
        valuations = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 15))]
        )
        self.assertFalse(valuations)

    @freeze_time("2024-02-29")
    def test_run_month_end_valuation_leap_year(self):
        """Test that valuation runs on last day of February in leap year."""
        result = self.env["stock.valuation.historical"]._run_month_end_valuation()
        self.assertTrue(result)

        valuations = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 2, 29))]
        )
        self.assertTrue(valuations)

    @freeze_time("2024-01-31")
    def test_create_month_end_valuation(self):
        """Test creating month-end valuations."""
        result = self.env["stock.valuation.historical"]._create_month_end_valuation()
        self.assertTrue(result)

        valuations = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 31))]
        )
        self.assertIn(self.product1, valuations.mapped("product_id"))
        self.assertIn(self.product2, valuations.mapped("product_id"))

        # Check product1 valuation
        val1 = valuations.filtered(lambda v: v.product_id == self.product1)
        self.assertTrue(val1)
        self.assertEqual(val1.quantity, 10.0)
        self.assertEqual(val1.warehouse_id, self.warehouse)
        self.assertEqual(val1.valuation_account_id, self.stock_valuation_account)

        # Check product2 valuation
        val2 = valuations.filtered(lambda v: v.product_id == self.product2)
        self.assertTrue(val2)
        self.assertEqual(val2.quantity, 5.0)

    @freeze_time("2024-01-31")
    def test_create_month_end_valuation_duplicate_prevention(self):
        """Test that duplicate valuations for same date are prevented."""
        # Create first valuation
        self.env["stock.valuation.historical"]._create_month_end_valuation()
        valuations1 = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 31))]
        )
        count1 = len(valuations1)

        # Try to create again
        self.env["stock.valuation.historical"]._create_month_end_valuation()
        valuations2 = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 31))]
        )
        count2 = len(valuations2)

        # Should have same count (duplicates deleted and recreated)
        self.assertEqual(count1, count2)

    @freeze_time("2024-01-31")
    def test_create_month_end_valuation_no_quants(self):
        """Test that no valuations are created when there are no quants."""
        # Remove all quants
        self.env["stock.quant"].search([]).unlink()

        result = self.env["stock.valuation.historical"]._create_month_end_valuation()
        self.assertFalse(result)

    @freeze_time("2024-01-31")
    def test_create_month_end_valuation_specific_company(self):
        """Test creating valuations for specific company."""
        result = self.env["stock.valuation.historical"]._create_month_end_valuation(
            companies=self.company
        )
        self.assertTrue(result)

        valuations = self.env["stock.valuation.historical"].search(
            [("date", "=", date(2024, 1, 31)), ("company_id", "=", self.company.id)]
        )
        self.assertTrue(valuations)

    @freeze_time("2024-01-31")
    def test_prepare_valuation_lines(self):
        """Test preparing valuation lines from quants."""
        lines = self.env["stock.valuation.historical"]._prepare_valuation_lines()
        self.assertTrue(lines)

        # Should have lines for both products
        product_ids = [line["product_id"] for line in lines]
        self.assertIn(self.product1.id, product_ids)
        self.assertIn(self.product2.id, product_ids)

        # Check structure of a line
        line = lines[0]
        self.assertIn("date", line)
        self.assertIn("company_id", line)
        self.assertIn("product_id", line)
        self.assertIn("warehouse_id", line)
        self.assertIn("quantity", line)
        self.assertIn("value", line)
        self.assertIn("valuation_account_id", line)
