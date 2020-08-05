# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestProductPriceChangeLine(TransactionCase):
    def setUp(self):
        super(TestProductPriceChangeLine, self).setUp()
        self.product_price_change = self.env.ref(
            "product_list_price_change" ".product_price_change_demo_1"
        )
        self.test_product_template_11 = self.env.ref(
            "product.product_product_11_product_template"
        )
        self.test_product_template_2 = self.env.ref(
            "product.product_product_10_product_template"
        )

    def test_onchange(self):
        ppc_form = Form(self.product_price_change)
        with ppc_form.product_line_ids.new() as test_new_ppcl:
            # test onchange product_tmpl_id
            test_new_ppcl.product_tmpl_id = self.test_product_template_2
            self.assertEqual(
                test_new_ppcl.list_price, self.test_product_template_2.list_price
            )
            test_new_ppcl.product_tmpl_id = self.test_product_template_11
            self.assertEqual(
                test_new_ppcl.list_price, self.test_product_template_11.list_price
            )
            # test onchange percent_change
            test_new_ppcl.percent_change = 10.0
            self.assertEqual(
                test_new_ppcl.list_price,
                self.test_product_template_11.list_price * 1.10,
            )
            # test onchange list_price
            test_new_ppcl.list_price = 50.0
            self.assertEqual(
                test_new_ppcl.percent_change,
                (
                    (
                        test_new_ppcl.list_price
                        / self.test_product_template_11.list_price
                    )
                    - 1
                )
                * 100.0,
            )
        ppc_form.save()
