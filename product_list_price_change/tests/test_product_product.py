# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestProductProduct(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_uom_unit = self.env.ref("uom.product_uom_unit")
        self.test_uom_dozen = self.env.ref("uom.product_uom_dozen")

        self.product_attr = self.env["product.attribute"].create(
            {"name": "PP Test Attr"}
        )
        self.attr_val = self.env["product.attribute.value"].create(
            {"name": "PP Val A", "attribute_id": self.product_attr.id}
        )
        self.product_tmpl = self.env["product.template"].create(
            {
                "name": "PP Test Product",
                "list_price": 5.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.product_attr.id,
                            "value_ids": [Command.link(self.attr_val.id)],
                        }
                    )
                ],
            }
        )
        self.product_product = self.product_tmpl.product_variant_ids[0]
        self.ptav = self.product_tmpl.attribute_line_ids.product_template_value_ids[0]

        self.product_price_change = self.env["product.price.change"].create(
            {
                "name": "PP Test Change",
                "effective_date": fields.Date.today(),
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": self.product_tmpl.id,
                            "list_price": 10.0,
                        }
                    )
                ],
                "variant_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_attribute_value_id": self.ptav.id,
                            "price_extra": 10.0,
                        }
                    )
                ],
            }
        )

    def test_compute_product_price_extra(self):
        self.product_price_change.state = "future"
        expected = 10.0
        unit_product = self.product_product.with_context(uom=self.test_uom_unit.id)
        dozen_product = self.product_product.with_context(uom=self.test_uom_dozen.id)
        self.assertEqual(expected, unit_product.price_extra)
        self.product_product.invalidate_recordset()
        expected = 10.0 * 12
        self.assertEqual(expected, dozen_product.price_extra)

    def test_compute_product_list_price(self):
        self.product_price_change.state = "future"
        unit_product = self.product_product.with_context(uom=self.test_uom_unit.id)
        dozen_product = self.product_product.with_context(uom=self.test_uom_dozen.id)
        # list_price from change (10.0) + price_extra from change (10.0) = 20.0
        expected_list_price = 20.0
        self.assertEqual(expected_list_price, unit_product.lst_price)
        self.product_product.invalidate_recordset()
        expected_list_price = 20.0 * 12
        self.assertEqual(expected_list_price, dozen_product.lst_price)

    def test_update_empty_price_change_records(self):
        products = self.env["product.template"].search(
            [("price_change_line_ids", "=", False)]
        )
        if products:
            self.env["product.template"]._update_templates_without_price_change()
            self.assertFalse(
                self.env["product.template"].search(
                    [("price_change_line_ids", "=", False)]
                )
            )
