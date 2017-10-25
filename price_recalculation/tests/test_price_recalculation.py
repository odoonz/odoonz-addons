
import logging
from odoo.addons.sale.tests import TestSale
from . import hypothesis_params as hp

_logger = logging.Logger(__name__)

try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError as err:
    _logger.debug(err)


class TestPriceCalculation(TestSale):

    def setUp(self):
        """Initial Setup"""
        super(TestPriceCalculation, self).setUp()
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': p.name, 'product_id': p.id, 'product_uom_qty': 2,
                'product_uom': p.uom_id.id, 'price_unit': p.list_price})
                           for p in self.products.values()],
            'pricelist_id': self.env.ref('product.list0').id,
        })

    def test_defaults(self):
        spr = self.env['price.recalculation'].with_context(
            active_ids=[self.so.id], active_model='sale.order').create()
        self.assertEqual(spr.name, self.so)
        self.assertEqual(spr.partner_id, self.so.partner_id)
        self.assertEqual(spr.date_order, self.so.date_order)


    # Put tests here
    @given(st.streaming(st.floats(**QTY_ARGS)),
           st.streaming(st.floats(**PRICE_ARGS)),
           st.streaming(st.floats(**DISCOUNT_ARGS)),
           st.floats(**PRICE_ARGS))
    def test_recalc(self, qty, price, discount, total):
        """
        When we create record check that it
        is correctly defaulted
        """
        so, recalc = self.create_so_and_recalc(qty, price, discount)
        start = len(self.products) + 1
        # We check the fields are set as expected
        self.assertEqual(recalc.name, so.id)
        self.assertEqual(recalc.partner_id, so.partner_id)
        self.assertEqual(len(so.order_line), len(recalc.line_ids))
        for l in recalc.line_ids:
            s = l.name
            self.assertEqual(s.product_id, l.product_id)
            self.assertEqual(s.product_uom_qty, l.qty)
            self.assertEqual(s.price_unit, l.price_unit)
            self.assertEqual(s.price_subtotal, l.price_subtotal)
            self.assertEqual(s.price_total, l.price_total)
            self.assertEqual(
                (s.price_total - s.price_subtotal) / s.price_subtotal,
                (l.price_total - l.price_subtotal) / l.price_subtotal)

        # We test that when we change the total ex tax that
        # the sum of the lines is equal to the total
        recalc.tax_incl = False
        recalc.total = total
        recalc._onchange_balance_to_total()
        self.assertEqual(sum([l.price_subtotal for l in recalc.line_ids]),
                         recalc.total)

        # We test that the pricing is roughly weighted in proportion
        approx_change = so.price_subtotal / recalc.total
        for l in recalc.line_ids:
            s = l.name
            self.assertAlmostEqual(
                s.price_subtotal / l.price_subtotal,
                approx_change, delta=0.1)

        # We test that when we change the total incl tax that
        # the sum of the lines is equal to the total
        recalc.tax_incl = True
        recalc.total = total
        recalc._onchange_balance_to_total()
        self.assertAlmostEqual(sum([l.price_total for l in recalc.line_ids]),
                               recalc.total, delta=0.02)

        # We test that the pricing is roughly weighted in proportion
        approx_change = so.price_total / recalc.total
        for l in recalc.line_ids:
            s = l.name
            self.assertAlmostEqual(
                s.price_total / l.price_total,
                approx_change, delta=0.1)

        # Test the changing a subtotal works correctly
        l = recalc.line_ids[:-1]
        l.price_total = price[start] * 100
        start += 1
        check_total = l.price_subtotal
        l._onchange_total()
        self.assertAlmostEqual(l.price_total, check_total, delta=1)
        self.assertEqual(l.price_subtotal, l.price_unit * l.price_qty)

        # Test the changing a subtotal works correctly
        # need to allow discounts
        l = recalc.line_ids[0]
        l.price_subtotal = price[start] * 100
        start += 1
        subtotal = l.price_subtotal
        l._onchange_subtotal()
        self.assertAlmostEqual(l.price_subtotal, subtotal, delta=1)
        self.assertEqual(l.price_subtotal, l.price_unit * l.price_qty)

        # Need to test copying from quote

        # We update the list price of products to random values
        # and test the unit prices have updated
        for i, p in enumerate(self.products.values(), start=start):
            p.list_price = price[i]
        recalc.pricelist_id = self.env.ref('product.list0')
        recalc._onchange_pricelist_id()
        for l in recalc.line_ids:
            self.assertEqual(l.price_unit, l.product_id.list_price)

        # When we write the order

    def test_06_action_priced(self):
        """
        When we write the records is the sale order updated
        and priced set to true
        """

    def test_07_action_write_correct(self):
        """
        When we write the records is the sale order
        updated
        """

    def test_08_action_write_constraint(self):
        """
        When we try to update a sale with a confirmed invoice
        do we get an error
        """

    @given(st.floats(**PRICE_ARGS), st.floats(**DISCOUNT_ARGS))
    def test_09_onchange_price_line(self, price, discount):
        """
        When we change price and/or discount is total updated correctly
        """

    @given(st.floats(**PRICE_ARGS))
    def test_10_onchange_total(self, total):
        """
        When we change total, is discount removed
        and qty x price = subtotal
        and subtotal x tax rate = total
        :param total: an incl_tax amount
        :return:
        """

    @given(st.floats(**PRICE_ARGS))
    def test_11_onchange_subtotal(self, subtotal):
        """
        When we change total, is discount removed
        and qty x price = subtotal
        and subtotal x tax rate = total
        :param subtotal: an excl_tax amount
        :return:
        """
