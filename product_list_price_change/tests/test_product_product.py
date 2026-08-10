# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

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


class TestProductProductPartnerContextCache(TransactionCase):
    """Regression tests for the ``partner_id`` cache-poisoning bug.

    Before ``_compute_product_lst_price``/``_compute_partner_effective_date``
    declared ``partner_id`` as a ``depends_context``, the ORM cache key did
    not vary with it. Reading the same record with different ``partner_id``
    contexts inside a single transaction (no cache invalidation in between)
    would silently return the price/date computed for whichever context was
    read *first*, poisoning the second read.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delayed_category = cls.env["res.partner.category"].create(
            {"name": "Delayed Pricing Category"}
        )
        cls.delayed_partner = cls.env["res.partner"].create(
            {
                "name": "Delayed Pricing Partner",
                "category_id": [Command.link(cls.delayed_category.id)],
            }
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {"name": "Partner Cache Test Product", "list_price": 50.0}
        )
        cls.product = cls.product_tmpl.product_variant_ids[0]

        cls.price_change = cls.env["product.price.change"].create(
            {
                "name": "Partner Cache Test Change",
                "effective_date": fields.Date.today() - timedelta(days=1),
                "state": "live",
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": cls.product_tmpl.id,
                            "list_price": 10.0,
                        }
                    )
                ],
            }
        )
        cls.env["product.price.change.implementation_delay"].create(
            {
                "name": "Delay for tagged category",
                "effective_date": fields.Date.today() + timedelta(days=1),
                "price_change_id": cls.price_change.id,
                "included_categories": [Command.link(cls.delayed_category.id)],
            }
        )

    def test_partner_effective_date_order_independent(self):
        no_partner = self.price_change.partner_effective_date
        self.assertEqual(no_partner, self.price_change.effective_date)
        delayed = self.price_change.with_context(
            partner_id=self.delayed_partner.id
        ).partner_effective_date
        self.assertNotEqual(delayed, no_partner)

        # Reverse the read order, without invalidating in between, to make
        # sure neither context's result leaks into the other.
        self.price_change.invalidate_recordset()
        delayed_first = self.price_change.with_context(
            partner_id=self.delayed_partner.id
        ).partner_effective_date
        no_partner_second = self.price_change.partner_effective_date
        self.assertEqual(delayed_first, delayed)
        self.assertEqual(no_partner_second, no_partner)

    def test_lst_price_order_independent(self):
        undelayed_price = self.product.lst_price
        self.assertEqual(undelayed_price, 10.0)

        delayed_price = self.product.with_context(
            partner_id=self.delayed_partner.id
        ).lst_price
        self.assertEqual(delayed_price, 50.0)

        # Reverse the read order, without invalidating in between, to make
        # sure neither context's result leaks into the other.
        self.product.invalidate_recordset()
        delayed_price_first = self.product.with_context(
            partner_id=self.delayed_partner.id
        ).lst_price
        undelayed_price_second = self.product.lst_price
        self.assertEqual(delayed_price_first, delayed_price)
        self.assertEqual(undelayed_price_second, undelayed_price)
