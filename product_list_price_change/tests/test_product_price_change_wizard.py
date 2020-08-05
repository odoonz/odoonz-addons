# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductPriceChangeWizard(TransactionCase):
    def setUp(self):
        super(TestProductPriceChangeWizard, self).setUp()
        self.product_price_change = self.env.ref(
            "product_list_price_change" ".product_price_change_demo_1"
        )
        self.ppc_wizard = self.env["product.price.change.wizard"].create(
            {
                "price_change_id": self.product_price_change.id,
                "product_tmpl_ids": [
                    self.env.ref("product.product_product_11_product_template").id
                ],
                "percent_change": 0.1,
            }
        )

    def test_compute_product_price_extra(self):
        # test raise validation error
        self.ppc_wizard.overwrite_existing = False
        with self.assertRaises(ValidationError):
            self.ppc_wizard.update_price_change_record()

        # test overwrite existing line
        self.ppc_wizard.overwrite_existing = True
        num_of_ppcl = self.env["product.price.change.line"].search_count(
            [("price_change_id", "=", self.product_price_change.id)]
        )
        self.assertTrue(num_of_ppcl, 1)

        # test add a new line
        self.ppc_wizard["product_tmpl_ids"] = self.env.ref(
            "product.product_product_10_product_template"
        )
        self.ppc_wizard.update_price_change_record()
        num_of_ppcl = self.env["product.price.change.line"].search_count(
            [("price_change_id", "=", self.product_price_change.id)]
        )
        self.assertTrue(num_of_ppcl, 2)
