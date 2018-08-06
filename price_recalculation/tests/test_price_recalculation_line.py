# Copyright 2107 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo.tests.common import TransactionCase
from odoo.tools import float_round
from . import hypothesis_params as hp

_logger = logging.Logger(__name__)

try:
    from hypothesis import given
    from hypothesis import strategies as st
    from hypothesis import assume
except ImportError as err:
    _logger.debug(err)


class TestPriceRecalculationLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.datacard = self.env.ref("product.product_delivery_02")

    @given(st.data())
    def test_onchange_total(self, data):
        qty = data.draw(st.floats(**hp.QTY_ARGS))
        price = data.draw(st.floats(**hp.PRICE_ARGS))
        tax_rate = data.draw(st.floats(**hp.TAX_ARGS))
        subtotal = data.draw(st.floats(**hp.PRICE_ARGS))
        total = data.draw(st.floats(**hp.PRICE_ARGS))
        assume(
            (subtotal > 0.10 or subtotal == 0.0)
            and (total > 0.10 or total == 0.0)
        )
        # assumed because of limitations in test rounding more than anything
        assume(float_round(tax_rate, 2) != -1.0)
        # impossible value which will give div / 0
        line = self.env["price.recalculation.line"].new(
            {
                "product_id": self.datacard.id,
                "qty": qty,
                "price_unit": price,
                "effective_tax_rate": tax_rate,
                "total": price * qty * (1 + tax_rate),
                "subtotal": price * qty,
            }
        )
        with self.env.do_in_onchange():
            line.total = float_round(total, 2)
            line._onchange_total()
            self.assertAlmostEqual(
                line.qty, qty, 2, "Changing totals should not affect qty"
            )
            self.assertAlmostEqual(
                line.price_subtotal * (1 + tax_rate), line.total, delta=0.01
            )
            expected = line.qty * line.price_unit
            self.assertAlmostEqual(expected, line.price_subtotal, delta=0.01)

            line.price_subtotal = float_round(subtotal, 2)
            line._onchange_subtotal()
            self.assertAlmostEqual(
                line.qty, qty, 2, "Changing totals should not affect qty"
            )
            self.assertAlmostEqual(
                line.price_subtotal * (1 + tax_rate), line.total, delta=0.01
            )
            self.assertAlmostEqual(
                line.qty * line.price_unit, line.price_subtotal, delta=0.01
            )
