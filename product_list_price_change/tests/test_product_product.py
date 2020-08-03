# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductProduct(TransactionCase):
    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.product_price_change = self.env.ref(
            "product_list_price_change" ".product_price_change_demo_1"
        )
        self.product_product_10 = self.env.ref("product.product_product_10")
        self.attribute_value = self.env.ref("product.product_4_attribute_1_value_2")

        self.test_uom_unit = self.env.ref("uom.product_uom_unit")
        self.test_uom_dozen = self.env.ref("uom.product_uom_dozen")

    def test_compute_product_price_extra(self):
        self.product_price_change.state = "future"
        self.product_product_10.update(
            {"product_template_attribute_value_ids": self.attribute_value}
        )
        expected = 10.0
        unit_product = self.product_product_10.with_context(uom=self.test_uom_unit.id)
        dozen_product = self.product_product_10.with_context(uom=self.test_uom_dozen.id)
        self.assertEqual(expected, unit_product.price_extra)
        self.product_product_10.invalidate_cache()
        expected = 10.0 * 12
        self.assertEqual(expected, dozen_product.price_extra)

    def test_compute_product_list_price(self):
        self.product_price_change.state = "future"
        self.product_product_10.update(
            {
                "list_price": 5.0,
                "product_template_attribute_value_ids": self.attribute_value,
            }
        )
        unit_product = self.product_product_10.with_context(uom=self.test_uom_unit.id)
        dozen_product = self.product_product_10.with_context(uom=self.test_uom_dozen.id)
        expected_list_price = 15.0
        self.assertEqual(expected_list_price, unit_product.lst_price)
        self.product_product_10.invalidate_cache()
        expected_list_price = 15.0 * 12
        self.assertEqual(expected_list_price, dozen_product.lst_price)
