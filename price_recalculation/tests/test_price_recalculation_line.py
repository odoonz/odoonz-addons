# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tests import common, tagged
from odoo.tools import float_round

from . import hypothesis_params as hp

_logger = logging.getLogger(__name__)

try:
    from hypothesis import assume, given, settings
    from hypothesis import strategies as st

    settings.register_profile("ci", database=None)
    settings.load_profile("ci")
except ImportError as err:
    _logger.debug(err)


@tagged("post-install", "-at-install")
class TestPriceRecalculationLine(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = self.env["price.recalculation.line"]
        self.product_category = self.env["product.category"].create(
            {
                "name": "Office Furniture",
            }
        )
        self.datacard = self.env["product.product"].create(
            {
                "name": "Office Lamp",
                "categ_id": self.product_category.id,
                "standard_price": 35.0,
                "list_price": 40.0,
                "type": "consu",
                "weight": 0.01,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "FURN_8888",
                # Omitting the image field unless it's essential for your test
            }
        )

    @given(st.data())
    def test_onchange_total(self, data):
        """This function is actually tested in sale_price_recalculation"""
        if self.model._abstract:
            # self.skipTest(f"Skipping test for abstract model {self.model._name}.")
            # Just return to avoid hypothesis complaints
            _logger.warning(f"Skipping test for abstract model {self.model._name}.")
            return

        qty = data.draw(st.floats(**hp.QTY_ARGS))
        price = data.draw(st.floats(**hp.PRICE_ARGS))
        tax_rate = data.draw(st.floats(**hp.TAX_ARGS))
        subtotal = data.draw(st.floats(**hp.PRICE_ARGS))
        total = data.draw(st.floats(**hp.PRICE_ARGS))
        assume((subtotal > 0.10 or subtotal == 0.0) and (total > 0.10 or total == 0.0))
        # assumed because of limitations in test rounding more than anything
        assume(float_round(tax_rate, 2) != -1.0)
        # impossible value which will give div / 0

        line = self.env["price.recalculation.line"].new(
            {
                "product_id": self.datacard.id,
                "qty": qty,
                "price_unit": price,
                "effective_tax_rate": tax_rate,
                "price_total": price * qty * (1 + tax_rate),
                "price_subtotal": price * qty,
            }
        )

        line.price_total = float_round(total, 2)
        line._onchange_price_total()
        self.assertAlmostEqual(
            line.qty, qty, 2, "Changing totals should not affect qty"
        )
        self.assertAlmostEqual(
            line.price_subtotal * (1 + tax_rate), line.price_total, delta=0.01
        )
        expected = line.qty * line.price_unit
        self.assertAlmostEqual(expected, line.price_subtotal, delta=0.01)

        line.price_subtotal = float_round(subtotal, 2)
        line._onchange_subtotal()
        self.assertAlmostEqual(
            line.qty, qty, 2, "Changing totals should not affect qty"
        )
        self.assertAlmostEqual(
            line.price_subtotal * (1 + tax_rate), line.price_total, delta=0.01
        )
        self.assertAlmostEqual(
            line.qty * line.price_unit, line.price_subtotal, delta=0.01
        )
