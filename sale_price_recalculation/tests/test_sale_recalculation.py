from random import randint, random
from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo import fields
from odoo.tools import float_compare as fc

import logging
import mock

pricelist = "odoo.addons.product.models.product_pricelist.Pricelist"
_logger = logging.Logger(__name__)


class TestSaleRecalc(TestSale):
    def setUp(self):
        super().setUp()
        today = fields.Date.to_string(fields.Date.context_today(self.partner))
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        self.so = (
            self.env["sale.order"]
            .with_context(context_no_mail)
            .create(
                {
                    "partner_id": self.partner.id,
                    "partner_invoice_id": self.partner.id,
                    "partner_shipping_id": self.partner.id,
                    "date_order": today,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": p.name,
                                "product_id": p.id,
                                "product_uom_qty": randint(1, 10),
                                "product_uom": p.uom_id.id,
                                "price_unit": randint(1, 100) / 2.1,
                                "discount": random() * 100.0,
                            },
                        )
                        for p in self.products.values()
                    ],
                    "pricelist_id": self.env.ref("product.list0").id,
                }
            )
        )
        self.spr = self.env["sale.price.recalculation"].with_context(
            active_id=self.so.id, active_ids=[self.so.id], active_model="sale.order"
        )
        self.vals = self.spr.default_get(
            ["name", "partner_id", "date_order", "line_ids"]
        )

        self.pricelist = self.env.ref("product.list0").copy()

    def test_default_get(self):
        """
        When we create record check that it
        is correctly defaulted
        """
        vals = self.spr.default_get(["name", "partner_id", "date_order", "line_ids"])
        recalc = self.spr.create(vals)
        so = self.so
        self.assertEqual(recalc.name, so)
        self.assertEqual(recalc.partner_id, so.partner_id)
        self.assertEqual(len(so.order_line), len(recalc.line_ids))
        l = recalc.line_ids[randint(0, len(recalc.line_ids) - 1)]
        s = l.name
        self.assertEqual(s.product_id, l.product_id)
        self.assertEqual(s.product_uom_qty, l.qty)
        self.assertFalse(fc(s.price_unit, l.price_unit, 2))
        self.assertFalse(fc(s.price_subtotal, l.price_subtotal, 2))
        self.assertFalse(fc(s.price_total, l.price_total, 2))

    def test_protected_fields(self):
        protected_field = "price_unit"
        OrderLine = self.env["sale.order.line"].with_context(
            ignore_protected_fields=[protected_field]
        )
        fields = OrderLine._get_protected_fields()
        self.assertNotIn(protected_field, fields)

    def test_change_ex_tax_total(self):
        recalc = self.spr.create(self.vals)
        recalc.total = 1000.0
        recalc.tax_incl = False
        recalc._onchange_balance_to_total()

        self.assertAlmostEqual(
            sum(recalc.line_ids.mapped("price_subtotal")), recalc.total, delta=1
        )
        # We test that the pricing is roughly weighted in proportion
        approx_change = self.so.amount_untaxed / recalc.total
        for l in recalc.line_ids:
            s = l.name
            self.assertAlmostEqual(
                s.price_subtotal / l.price_subtotal, approx_change, delta=1
            )

    def test_change_inc_tax_total(self):
        # We test that when we change the total incl tax that
        # the sum of the lines is equal to the total
        recalc = self.spr.create(self.vals)
        recalc.tax_incl = True
        recalc.total = 1000.0
        recalc._onchange_balance_to_total()
        self.assertAlmostEqual(
            sum(recalc.line_ids.mapped("price_total")), recalc.total, delta=1.0
        )
        # We test that the pricing is roughly weighted in proportion
        approx_change = self.so.amount_total / recalc.total
        for l in recalc.line_ids:
            s = l.name
            self.assertAlmostEqual(
                s.price_total / l.price_total, approx_change, delta=1
            )

    def test_change_line_total(self):
        """Test the changing a subtotal works correctly"""
        line = self.env["sale.price.recalculation.line"].new()
        line.update(
            {
                "price_unit": 20.0,
                "discount": 10.0,
                "qty": 5.0,
                "price_subtotal": 90.0,
                "price_total": 108.0,
                "effective_tax_rate": 0.2,
            }
        )
        with self.env.do_in_onchange():
            check_total = 600.0
            line.price_total = check_total
            line._onchange_total()
            self.assertAlmostEqual(line.price_total, check_total, delta=1)
            self.assertFalse(fc(line.price_subtotal, line.price_unit * line.qty, 2))
            self.assertEqual(line.qty, 5.0, "Changing totals should not affect qty")
            self.assertFalse(fc(line.price_subtotal * (1 + 0.2), line.total, 2))
            self.assertEqual(line.discount, 0.0)

    def test_change_line_subtotal(self):
        """Test the changing a subtotal works correctly"""
        line = self.env["sale.price.recalculation.line"].new()
        line.update(
            {
                "price_unit": 20.0,
                "discount": 10.0,
                "qty": 5.0,
                "price_subtotal": 90.0,
                "price_total": 108.0,
                "effective_tax_rate": 0.2,
            }
        )
        with self.env.do_in_onchange():
            check_total = 721.0
            line.price_subtotal = check_total
            line._onchange_subtotal()
            self.assertAlmostEqual(line.price_subtotal, check_total, delta=1)
            self.assertAlmostEqual(
                line.price_subtotal, line.price_unit * line.qty, delta=0.01
            )
            self.assertEqual(line.qty, 5.0, "Changing totals should not affect qty")
            self.assertAlmostEqual(
                line.price_subtotal * (1 + 0.2), line.total, delta=0.01
            )
            self.assertEqual(line.discount, 0.0)

    def test_change_line_price(self):
        """Test the changing a subtotal works correctly"""
        line = self.env["sale.price.recalculation.line"].new()
        line.update(
            {
                "price_unit": 20.0,
                "discount": 0.0,
                "qty": 5.0,
                "price_subtotal": 90.0,
                "price_total": 108.0,
                "effective_tax_rate": 0.2,
            }
        )
        with self.env.do_in_onchange():
            check_total = 7.21
            line.price_unit = check_total
            line._onchange_price()
            self.assertFalse(fc(line.price_subtotal, line.price_unit * line.qty, 2))

    def test_onchange_pricelist_id(self):
        recalc = self.spr.create(self.vals)
        with mock.patch("%s.get_products_price" % pricelist) as price_get:
            prices = {
                p.id: round(random() * randint(1, 9), 2) for p in self.products.values()
            }
            price_get.return_value = prices
            with self.env.do_in_onchange():
                recalc.pricelist_id = self.pricelist
                recalc.onchange_pricelist_id()
            subtotal = 0.0
            for line in recalc.line_ids:
                self.assertFalse(fc(prices[line.product_id.id], line.price_unit, 2))
                subtotal += line.price_subtotal
            recalc.action_write()
        so = self.env["sale.order"].browse(self.so.id)
        self.assertFalse(fc(so.amount_untaxed, subtotal, 2))
        self.assertEqual(so.pricelist_id, recalc.pricelist_id)

    def test_onchange_quote_id(self):
        recalc = self.spr.create(self.vals)
        quote = self.so.copy()
        quote.pricelist_id = self.pricelist
        quote.order_line[0].price_unit = 1.66

        with self.env.do_in_onchange():
            recalc.copy_quote_id = quote
            recalc.onchange_quote_id()
        self.assertFalse(fc(recalc.line_ids[0].price_unit, 1.66, 2))
        recalc.action_write()
        self.assertEqual(self.so.pricelist_id, quote.pricelist_id)
        self.assertFalse(fc(self.so.order_line[0].price_unit, 1.66, 2))
