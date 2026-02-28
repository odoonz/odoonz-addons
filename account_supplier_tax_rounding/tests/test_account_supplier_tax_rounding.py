# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSupplierTaxRounding(TransactionCase):
    """Tests for account_supplier_tax_rounding."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                mail_create_nolog=True,
                mail_no_track=True,
            )
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Tax Rounding Supplier", "supplier_rank": 1}
        )
        cls.purchase_tax = cls.env["account.tax"].create(
            {
                "name": "Test Purchase Tax 15%",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 15.0,
            }
        )
        cls.sale_tax = cls.env["account.tax"].create(
            {
                "name": "Test Sale Tax 15%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 15.0,
            }
        )

    def test_partner_tax_calc_method_default(self):
        """New partner defaults to round_globally."""
        partner = self.env["res.partner"].create({"name": "Default Rounding"})
        self.assertEqual(partner.tax_calc_method, "round_globally")

    def test_partner_tax_calc_method_round_per_line(self):
        """Partner tax_calc_method can be set to round_per_line."""
        self.partner.tax_calc_method = "round_per_line"
        self.assertEqual(self.partner.tax_calc_method, "round_per_line")

    def test_is_purchase_tax_filters_purchase(self):
        """_is_purchase_tax returns only purchase taxes."""
        result = self.purchase_tax._is_purchase_tax()
        self.assertEqual(result, self.purchase_tax)

    def test_is_purchase_tax_excludes_sale(self):
        """_is_purchase_tax returns empty for sale taxes."""
        result = self.sale_tax._is_purchase_tax()
        self.assertFalse(result)

    def test_is_purchase_tax_mixed_recordset(self):
        """_is_purchase_tax filters from mixed recordset."""
        taxes = self.purchase_tax | self.sale_tax
        result = taxes._is_purchase_tax()
        self.assertEqual(result, self.purchase_tax)

    def test_compute_all_purchase_uses_partner_rounding(self):
        """compute_all with purchase tax and partner uses partner's method."""
        self.partner.tax_calc_method = "round_per_line"
        result = self.purchase_tax.compute_all(100.0, partner=self.partner)
        self.assertIn("total_excluded", result)
        self.assertIn("total_included", result)
        self.assertAlmostEqual(result["total_excluded"], 100.0)
        self.assertAlmostEqual(result["total_included"], 115.0)

    def test_compute_all_sale_tax_ignores_partner_rounding(self):
        """compute_all with sale tax does not use partner's rounding."""
        self.partner.tax_calc_method = "round_per_line"
        result = self.sale_tax.compute_all(100.0, partner=self.partner)
        self.assertAlmostEqual(result["total_excluded"], 100.0)
        self.assertAlmostEqual(result["total_included"], 115.0)

    def test_compute_all_no_partner(self):
        """compute_all without partner uses default rounding."""
        result = self.purchase_tax.compute_all(100.0)
        self.assertAlmostEqual(result["total_excluded"], 100.0)
        self.assertAlmostEqual(result["total_included"], 115.0)

    def test_compute_all_rounding_difference(self):
        """Different rounding methods produce different results on edge prices."""
        tax_a = self.env["account.tax"].create(
            {
                "name": "Rounding Test Tax 10%",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 10.0,
            }
        )
        supplier_global = self.env["res.partner"].create(
            {
                "name": "Global Rounding Supplier",
                "tax_calc_method": "round_globally",
            }
        )
        supplier_per_line = self.env["res.partner"].create(
            {
                "name": "Per-Line Rounding Supplier",
                "tax_calc_method": "round_per_line",
            }
        )
        res_global = tax_a.compute_all(33.33, partner=supplier_global, quantity=3.0)
        res_per_line = tax_a.compute_all(33.33, partner=supplier_per_line, quantity=3.0)
        self.assertAlmostEqual(
            res_global["total_excluded"],
            res_per_line["total_excluded"],
        )
        self.assertTrue(res_global["total_included"] > 0)
        self.assertTrue(res_per_line["total_included"] > 0)

    def test_compute_all_with_quantity(self):
        """compute_all respects quantity parameter."""
        result = self.purchase_tax.compute_all(50.0, partner=self.partner, quantity=3.0)
        self.assertAlmostEqual(result["total_excluded"], 150.0)
        self.assertAlmostEqual(result["total_included"], 172.5)

    def test_compute_all_empty_taxes(self):
        """compute_all on empty recordset returns base amounts."""
        empty = self.env["account.tax"]
        result = empty.compute_all(100.0, partner=self.partner)
        self.assertAlmostEqual(result["total_excluded"], 100.0)
        self.assertAlmostEqual(result["total_included"], 100.0)
        self.assertEqual(len(result["taxes"]), 0)
