# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from random import randint

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductPriceChange(TransactionCase):
    def setUp(self):
        super(TestProductPriceChange, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.product_price_change = self.env.ref(
            "product_list_price_change.product_price_change_demo_1"
        )
        self.implementation_delay = self.env.ref(
            "product_list_price_change.product_price_change_implementation_delay_demo_1"
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
        test_product_line = test_ppc.product_line_ids[
            randint(0, len(test_ppc.product_line_ids) - 1)
        ]
        test_variant_line = test_ppc.variant_line_ids[
            randint(0, len(test_ppc.variant_line_ids) - 1)
        ]
        self.assertEqual(
            test_product_line.list_price, test_product_line.product_tmpl_id.list_price
        )
        self.assertEqual(
            test_variant_line.price_extra,
            test_variant_line.product_tmpl_attribute_value_id.price_extra,
        )
