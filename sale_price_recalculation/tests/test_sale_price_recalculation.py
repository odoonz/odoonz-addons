import logging
import unittest.mock as mock
from collections import OrderedDict
from random import randint, random

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import Form, tagged
from odoo.tools import float_compare as fc, float_round

from odoo.addons.sale.tests.common import TestSaleCommon

from . import hypothesis_params as hp

_logger = logging.getLogger(__name__)

try:
    from hypothesis import assume, given, settings, strategies as st

    settings.register_profile("ci", database=None)
    settings.load_profile("ci")
except ImportError as err:
    _logger.debug(err)

pricelist = "odoo.addons.product.models.product_pricelist.Pricelist"


@tagged("post_install", "-at_install")
class TestSaleRecalc(TestSaleCommon):
    def setUp(self):
        super().setUp()
        self.products = OrderedDict(
            [
                ("prod_order_cost", self.company_data["product_order_cost"]),
                ("prod_del_cost", self.company_data["product_delivery_cost"]),
                (
                    "prod_order_sales_price",
                    self.company_data["product_order_sales_price"],
                ),
                (
                    "prod_del_sales_price",
                    self.company_data["product_delivery_sales_price"],
                ),
                ("prod_order_no", self.company_data["product_order_no"]),
                ("prod_del_no", self.company_data["product_delivery_no"]),
                ("serv_del", self.company_data["product_service_delivery"]),
                ("serv_order", self.company_data["product_service_order"]),
            ]
        )
        today = fields.Date.to_string(fields.Date.context_today(self.partner_a))
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        self.so = (
            self.env["sale.order"]
            .with_context(**context_no_mail)
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "partner_invoice_id": self.partner_a.id,
                    "partner_shipping_id": self.partner_a.id,
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
                    "pricelist_id": self.company_data["default_pricelist"].id,
                }
            )
        )
        self.spr = self.env["sale.price.recalculation"].with_context(
            active_id=self.so.id, active_ids=[self.so.id], active_model="sale.order"
        )
        self.vals = self.spr.default_get(
            ["name", "partner_id", "as_at_date", "line_ids"]
        )

        self.pricelist = self.company_data["default_pricelist"].copy()

    def test_access_spr(self):
        self.spr.with_user(self.company_data["default_user_salesman"]).create(self.vals)
        with self.assertRaises(AccessError):
            _logger.info('Expecting "Access Denied by ACLs"...')
            self.spr.with_user(self.company_data["default_user_employee"]).create(
                self.vals
            )
        with self.assertRaises(AccessError):
            _logger.info('Expecting "Access Denied by ACLs"...')
            self.spr.with_user(self.company_data["default_user_portal"]).create(
                self.vals
            )

    def test_default_get(self):
        """
        When we create record check that it
        is correctly defaulted
        """
        SaleOrderLine = self.env["sale.order.line"]
        Product = self.env["product.product"]

        vals = self.spr.default_get(["name", "partner_id", "as_at_date", "line_ids"])
        so = self.so

        # Test values returned by default_get()
        vals_lines = [line[2] for line in vals["line_ids"]]
        vals_line = vals_lines[randint(0, len(vals_lines) - 1)]
        sol = SaleOrderLine.browse(vals_line["name"])
        self.assertEqual(sol.order_id, so)
        product = Product.browse(vals_line["product_id"])
        self.assertEqual(sol.product_id, product)
        self.assertEqual(sol.product_uom_qty, vals_line["qty"])
        try:
            self.assertFalse(fc(sol.price_unit, vals_line["price_unit"], 2))
        except AssertionError:
            _logger.error(
                f"sol.price_unit: {sol.price_subtotal} !="
                f' vals_line["price_unit"]: {vals_line["price_subtotal"]}'
            )
            raise

        # Test created recalculation which should be using default_get()
        recalc = (
            self.spr.with_user(self.company_data["default_user_salesman"])
            .with_context(active_id=so.id, active_model=so._name)
            .create(vals)
        )
        self.assertEqual(recalc.name, so)
        self.assertEqual(recalc.as_at_date, so.date_order.date())
        self.assertEqual(recalc.partner_id, so.partner_id)
        self.assertEqual(len(so.order_line), len(recalc.line_ids))
        line = recalc.line_ids[randint(0, len(recalc.line_ids) - 1)]
        sol = line.name
        self.assertEqual(sol.product_id, line.product_id)
        self.assertEqual(sol.product_uom_qty, line.qty)
        self.assertFalse(fc(sol.price_unit, line.price_unit, 2))
        try:
            self.assertFalse(fc(sol.price_subtotal, line.price_subtotal, 2))
        except AssertionError:
            _logger.error(
                f"sol.price_subtotal: {sol.price_subtotal} !="
                f" line.price_subtotal: {line.price_subtotal}"
            )
            raise
        self.assertFalse(fc(sol.price_total, line.price_total, 2))

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
        for line in recalc.line_ids:
            s = line.name
            self.assertAlmostEqual(
                s.price_subtotal / line.price_subtotal, approx_change, delta=1
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
        for line in recalc.line_ids:
            s = line.name
            self.assertAlmostEqual(
                s.price_total / line.price_total, approx_change, delta=1
            )

    @given(st.data())
    def test_change_line_total(self, data):
        """Test the changing a subtotal works correctly"""
        subtotal = data.draw(st.floats(**hp.PRICE_ARGS))
        total = data.draw(st.floats(**hp.PRICE_ARGS))
        assume((subtotal > 0.10 or subtotal == 0.0) and (total > 0.10 or total == 0.0))
        # assumed because of limitations in test rounding more than anything

        with Form(self.spr) as spr:
            with spr.line_ids.edit(randint(0, len(spr.line_ids) - 1)) as line:
                line.discount = 10.0
                original_qty = line.qty
                check_total = float_round(total, 1)
                line.price_total = check_total
                self.assertAlmostEqual(line.price_total, check_total, delta=0.1)
                self.assertAlmostEqual(
                    line.qty * line.price_unit, line.price_subtotal, delta=0.01
                )
                self.assertAlmostEqual(
                    line.qty, original_qty, 2, "Changing totals should not affect qty"
                )
                self.assertAlmostEqual(
                    line.price_subtotal * (1 + line.effective_tax_rate),
                    line.price_total,
                    delta=0.01,
                )
                self.assertEqual(line.discount, 0.0)
        spr.save()

    @given(st.data())
    def test_change_line_subtotal(self, data):
        """Test the changing a subtotal works correctly"""
        subtotal = data.draw(st.floats(**hp.PRICE_ARGS))
        total = data.draw(st.floats(**hp.PRICE_ARGS))
        assume((subtotal > 0.10 or subtotal == 0.0) and (total > 0.10 or total == 0.0))
        # assumed because of limitations in test rounding more than anything

        with Form(self.spr) as spr:
            with spr.line_ids.edit(randint(0, len(spr.line_ids) - 1)) as line:
                line.discount = 10.0
                original_qty = line.qty
                check_total = float_round(subtotal, 1)
                line.price_subtotal = check_total
                self.assertAlmostEqual(line.price_subtotal, check_total, delta=0.1)
                self.assertAlmostEqual(
                    line.qty * line.price_unit, line.price_subtotal, delta=0.01
                )
                self.assertAlmostEqual(
                    line.qty, original_qty, 2, "Changing totals should not affect qty"
                )
                self.assertAlmostEqual(
                    line.price_subtotal * (1 + line.effective_tax_rate),
                    line.price_total,
                    delta=0.01,
                )
                self.assertEqual(line.discount, 0.0)
        spr.save()

    @given(st.data())
    def test_change_line_price(self, data):
        """Test the changing a unit price works correctly"""
        new_price_unit = float_round(
            data.draw(st.floats(**hp.PRICE_ARGS)),
            2,
        )

        with Form(self.spr) as spr:
            with spr.line_ids.edit(randint(0, len(spr.line_ids) - 1)) as line:
                discount_factor = (100.0 - line.discount) / 100.0
                expected_subtotal = float_round(
                    line.qty * new_price_unit * discount_factor, 2
                )
                line.price_unit = new_price_unit
                self.assertAlmostEqual(
                    line.price_subtotal, expected_subtotal, delta=0.01
                )
        spr.save()

    def test_onchange_pricelist_id(self):
        recalc = self.spr.create(self.vals)
        price_unit = 12.47
        with mock.patch.object(
            type(self.pricelist), "_get_product_price", return_value=price_unit
        ):
            with Form(recalc) as spr:
                spr.pricelist_id = self.pricelist
                for idx in range(len(spr.line_ids)):
                    with spr.line_ids.edit(idx) as line:
                        try:
                            self.assertFalse(fc(price_unit, line.price_unit, 2))
                        except AssertionError:
                            _logger.error(
                                f"price_unit: {price_unit} !="
                                f" line.price_unit: {line.price_unit}"
                            )
                            raise
        subtotal = sum(recalc.line_ids.mapped("price_subtotal"))
        recalc.action_write()
        so = self.env["sale.order"].browse(self.so.id)
        try:
            self.assertFalse(fc(so.amount_untaxed, subtotal, 2))
        except AssertionError:
            _logger.error(
                f"so.amount_untaxed: {so.amount_untaxed} != subtotal: {subtotal}"
            )
            raise
        self.assertEqual(so.pricelist_id, recalc.pricelist_id)

    def test_onchange_quote_id(self):
        recalc = self.spr.create(self.vals)
        quote = self.so.copy()
        quote.pricelist_id = self.pricelist
        quote.order_line[0].price_unit = 1.66
        quote.order_line[0].discount = 0.0
        with Form(recalc) as spr:
            spr.copy_quote_id = quote
            with spr.line_ids.edit(0) as line:
                self.assertFalse(fc(line.price_unit, 1.66, 2))
        recalc.action_write()
        self.assertEqual(self.so.pricelist_id, quote.pricelist_id)
        self.assertFalse(fc(self.so.order_line[0].price_unit, 1.66, 2))
