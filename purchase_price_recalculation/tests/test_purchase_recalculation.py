# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from random import randint

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests.common import Form, TransactionCase
from odoo.tools import float_compare as fc, float_round

from . import hypothesis_params as hp

_logger = logging.Logger(__name__)
try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError as err:
    _logger.debug(err)


class TestPurchaseOrder(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        self.PurchaseOrder = self.env["purchase.order"]

        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        (self.product_id_1 | self.product_id_2).write({"purchase_method": "purchase"})
        po_date = fields.Datetime.to_string(fields.Datetime.now(self.product_id_1))
        po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": po_date,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": po_date,
                    },
                ),
            ],
        }

        self.po = self.PurchaseOrder.with_context(context_no_mail).create(po_vals)
        self.po.button_confirm()

        self.ppr = self.env["purchase.price.recalculation"].with_context(
            active_id=self.po.id, active_ids=[self.po.id], active_model="purchase.order"
        )
        self.vals = self.ppr.default_get(
            ["name", "partner_id", "date_order", "line_ids"]
        )

    def test_access_ppr(self):
        user = self.env.user.copy()
        user.groups_id = [(6, 0, [self.env.ref("purchase.group_purchase_user").id])]
        self.ppr.with_user(user).create(self.vals)
        user.groups_id = [(6, 0, [self.env.ref("sales_team.group_sale_salesman").id])]
        with self.assertRaises(AccessError):
            self.ppr.with_user(user).create(self.vals)

    def test_default_get(self):
        """
        When we create record check that it
        is correctly defaulted
        """
        vals = self.ppr.default_get(["name", "partner_id", "date_order", "line_ids"])
        recalc = self.ppr.create(vals)
        po = self.po
        self.assertEqual(recalc.name, po)
        self.assertEqual(recalc.partner_id, po.partner_id)
        self.assertEqual(len(po.order_line), len(recalc.line_ids))
        line = recalc.line_ids[randint(0, len(recalc.line_ids) - 1)]
        pol = line.name
        self.assertEqual(pol.product_id, line.product_id)
        self.assertEqual(pol.product_qty, line.qty)
        self.assertFalse(fc(pol.price_unit, line.price_unit, 2))
        self.assertFalse(fc(pol.price_subtotal, line.price_subtotal, 2))
        self.assertFalse(fc(pol.price_total, line.price_total, 2))

    def test_change_ex_tax_total(self):
        recalc = self.ppr.create(self.vals)
        recalc.total = 1000.0
        recalc.tax_incl = False
        recalc._onchange_balance_to_total()

        self.assertAlmostEqual(
            sum(recalc.line_ids.mapped("price_subtotal")), recalc.total, delta=1
        )
        # We test that the pricing is roughly weighted in proportion
        approx_change = self.po.amount_untaxed / recalc.total
        subtotal = 0.0
        for line in recalc.line_ids:
            p = line.name
            self.assertAlmostEqual(
                p.price_subtotal / line.price_subtotal, approx_change, delta=1
            )
            subtotal += line.price_subtotal
        recalc.action_write()
        self.assertFalse(fc(self.po.amount_untaxed, subtotal, 2))

    @given(st.data())
    def test_change_line_price(self, data):
        """Test the changing a subtotal works correctly"""
        price = data.draw(st.floats(**hp.PRICE_ARGS))
        with Form(self.ppr) as ppr:
            with ppr.line_ids.edit(randint(0, len(ppr.line_ids) - 1)) as line:
                check_total = float_round(price, 1)
                line.price_unit = check_total
                self.assertAlmostEqual(
                    line.qty * line.price_unit, line.price_subtotal, delta=0.01
                )
