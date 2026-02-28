# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductPriceChange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_category = cls.env["res.partner.category"].create(
            {"name": "Price Test Category"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Price Change Test Partner",
                "category_id": [Command.link(cls.partner_category.id)],
            }
        )

        cls.product_attr = cls.env["product.attribute"].create(
            {"name": "PPC Test Attr"}
        )
        cls.attr_val_a = cls.env["product.attribute.value"].create(
            {"name": "Val A", "attribute_id": cls.product_attr.id}
        )
        cls.attr_val_b = cls.env["product.attribute.value"].create(
            {"name": "Val B", "attribute_id": cls.product_attr.id}
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "PPC Test Product",
                "list_price": 50.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.product_attr.id,
                            "value_ids": [
                                Command.link(cls.attr_val_a.id),
                                Command.link(cls.attr_val_b.id),
                            ],
                        }
                    )
                ],
            }
        )
        cls.ptav = cls.product_tmpl.attribute_line_ids.product_template_value_ids[0]

        cls.product_price_change = cls.env["product.price.change"].create(
            {
                "name": "Test Price Rise",
                "effective_date": fields.Date.today(),
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": cls.product_tmpl.id,
                            "list_price": 10.0,
                        }
                    )
                ],
                "variant_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_attribute_value_id": cls.ptav.id,
                            "price_extra": 10.0,
                        }
                    )
                ],
            }
        )

        cls.implementation_delay = cls.env[
            "product.price.change.implementation_delay"
        ].create(
            {
                "name": "Delayed Implementation",
                "effective_date": fields.Date.today(),
                "price_change_id": cls.product_price_change.id,
                "included_categories": [Command.link(cls.partner_category.id)],
            }
        )

    def test_actions(self):
        self.product_price_change.state = "draft"
        self.product_price_change.action_confirm()
        self.assertTrue(self.product_price_change.state, "future")
        self.product_price_change.action_cancel()
        self.assertTrue(self.product_price_change.state, "cancel")
        self.product_price_change.action_draft()
        self.assertTrue(self.product_price_change.state, "draft")
        self.product_price_change.state = "live"
        with self.assertRaises(UserError):
            self.product_price_change.action_cancel()
        with self.assertRaises(UserError):
            self.product_price_change.action_draft()

    def test_compute_partner_effective_date(self):
        self.assertEqual(
            self.product_price_change.partner_effective_date,
            self.product_price_change.effective_date,
        )
        self.product_price_change.invalidate_recordset()
        self.assertEqual(
            self.product_price_change.with_context(
                partner_id=self.partner.id
            ).partner_effective_date,
            self.implementation_delay.effective_date,
        )

    def test_perform_list_price_update(self):
        test_ppc = self.product_price_change
        test_ppc.state = "future"
        test_ppc.perform_list_price_update()
        test_product_line = test_ppc.product_line_ids[0]
        test_variant_line = test_ppc.variant_line_ids[0]
        self.assertEqual(
            test_product_line.list_price, test_product_line.product_tmpl_id.list_price
        )
        self.assertEqual(
            test_variant_line.price_extra,
            test_variant_line.product_tmpl_attribute_value_id.price_extra,
        )
