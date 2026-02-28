# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests.common import Form, TransactionCase


class TestProductPriceChangeLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_product_template_a = self.env["product.template"].create(
            {"name": "PPCL Test Product A", "list_price": 100.0}
        )
        self.test_product_template_b = self.env["product.template"].create(
            {"name": "PPCL Test Product B", "list_price": 200.0}
        )
        self.product_price_change = self.env["product.price.change"].create(
            {
                "name": "PPCL Test Change",
                "effective_date": fields.Date.today(),
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": self.test_product_template_a.id,
                            "list_price": 110.0,
                        }
                    )
                ],
            }
        )

    def test_onchange(self):
        ppc_form = Form(self.product_price_change)
        with ppc_form.product_line_ids.new() as test_new_ppcl:
            test_new_ppcl.product_tmpl_id = self.test_product_template_b
            self.assertEqual(
                test_new_ppcl.list_price, self.test_product_template_b.list_price
            )
            test_new_ppcl.product_tmpl_id = self.test_product_template_a
            self.assertEqual(
                test_new_ppcl.list_price, self.test_product_template_a.list_price
            )
            test_new_ppcl.percent_change = 10.0
            self.assertAlmostEqual(
                test_new_ppcl.list_price,
                self.test_product_template_a.list_price * 1.10,
                places=2,
            )
            test_new_ppcl.list_price = 50.0
            self.assertEqual(
                test_new_ppcl.percent_change,
                (
                    (test_new_ppcl.list_price / self.test_product_template_a.list_price)
                    - 1
                )
                * 100.0,
            )
        ppc_form.save()
