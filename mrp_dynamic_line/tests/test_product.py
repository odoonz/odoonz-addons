# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestProductBomFields(TestMrpCommon):
    """Tests for product.product and product.template BoM-related methods."""

    def test_compute_used_in_bom_count_product(self):
        """_compute_used_in_bom_count counts BoMs using this product."""
        product = self.bom_1.bom_line_ids[0].product_id
        product._compute_used_in_bom_count()
        self.assertGreaterEqual(product.used_in_bom_count, 1)

    def test_compute_used_in_bom_count_product_no_bom(self):
        """_compute_used_in_bom_count is 0 for product not in any BoM."""
        product = self.env["product.product"].create({"name": "No-BoM Product"})
        product._compute_used_in_bom_count()
        self.assertEqual(product.used_in_bom_count, 0)

    def test_action_used_in_bom_product(self):
        """action_used_in_bom returns action with correct domain."""
        product = self.bom_1.bom_line_ids[0].product_id
        action = product.action_used_in_bom()
        self.assertIn("domain", action)
        self.assertEqual(
            action["domain"],
            [
                (
                    "bom_line_ids.product_tmpl_id",
                    "=",
                    product.product_tmpl_id.id,
                )
            ],
        )

    def test_compute_used_in_bom_count_template(self):
        """_compute_used_in_bom_count on template counts BoMs."""
        tmpl = self.bom_1.bom_line_ids[0].product_tmpl_id
        tmpl._compute_used_in_bom_count()
        self.assertGreaterEqual(tmpl.used_in_bom_count, 1)

    def test_action_used_in_bom_template(self):
        """action_used_in_bom on template returns correct domain."""
        tmpl = self.bom_1.bom_line_ids[0].product_tmpl_id
        action = tmpl.action_used_in_bom()
        self.assertIn("domain", action)
        self.assertEqual(
            action["domain"],
            [("bom_line_ids.product_tmpl_id", "=", tmpl.id)],
        )

    def test_compute_bom_price(self):
        """_compute_bom_price delegates to _compute_bom_price_by_type."""
        product = (
            self.bom_1.product_id or self.bom_1.product_tmpl_id.product_variant_ids[0]
        )
        for line in self.bom_1.bom_line_ids:
            line.product_id.standard_price = 5.0
        price = product._compute_bom_price(self.bom_1)
        self.assertGreaterEqual(price, 0)

    def test_compute_bom_price_no_bom(self):
        """_compute_bom_price_by_type returns 0 when no BoM."""
        product = self.env["product.product"].create({"name": "No BoM Product 2"})
        price = product._compute_bom_price_by_type(False)
        self.assertEqual(price, 0)

    def test_compute_bom_price_by_type_with_raw_materials(self):
        """_compute_bom_price_by_type sums raw material costs."""
        product = (
            self.bom_1.product_id or self.bom_1.product_tmpl_id.product_variant_ids[0]
        )
        for line in self.bom_1.bom_line_ids:
            line.product_id.standard_price = 10.0
        price = product._compute_bom_price_by_type(self.bom_1)
        self.assertGreater(price, 0)
