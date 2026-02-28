# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductPriceChangeWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tmpl_a = self.env["product.template"].create(
            {"name": "Wizard Test A", "list_price": 100.0}
        )
        self.tmpl_b = self.env["product.template"].create(
            {"name": "Wizard Test B", "list_price": 200.0}
        )
        self.product_price_change = self.env["product.price.change"].create(
            {
                "name": "Wizard Test Change",
                "effective_date": fields.Date.today(),
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": self.tmpl_a.id,
                            "list_price": 110.0,
                        }
                    )
                ],
            }
        )
        self.ppc_wizard = self.env["product.price.change.wizard"].create(
            {
                "price_change_id": self.product_price_change.id,
                "product_tmpl_ids": [self.tmpl_a.id],
                "percent_change": 0.1,
            }
        )

    def test_compute_product_price_extra(self):
        self.ppc_wizard.overwrite_existing = False
        with self.assertRaises(ValidationError):
            self.ppc_wizard.update_price_change_record()

        self.ppc_wizard.overwrite_existing = True
        num_of_ppcl = self.env["product.price.change.line"].search_count(
            [("price_change_id", "=", self.product_price_change.id)]
        )
        self.assertTrue(num_of_ppcl, 1)

        self.ppc_wizard["product_tmpl_ids"] = self.tmpl_b
        self.ppc_wizard.update_price_change_record()
        num_of_ppcl = self.env["product.price.change.line"].search_count(
            [("price_change_id", "=", self.product_price_change.id)]
        )
        self.assertTrue(num_of_ppcl, 2)
