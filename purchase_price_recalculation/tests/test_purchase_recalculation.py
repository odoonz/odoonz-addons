# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.tools import float_compare as fc
from random import randint


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

        (self.product_id_1 | self.product_id_2).write(
            {"purchase_method": "purchase"}
        )
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
                        "date_planned": fields.Datetime.now(self.product_id_1),
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
                        "date_planned": fields.Datetime.now(self.product_id_1),
                    },
                ),
            ],
        }

        self.po = self.PurchaseOrder.with_context(context_no_mail).create(
            po_vals
        )
        self.po.button_confirm()

        self.ppr = self.env["purchase.price.recalculation"].with_context(
            active_id=self.po.id,
            active_ids=[self.po.id],
            active_model="purchase.order",
        )
        self.vals = self.ppr.default_get(
            ["name", "partner_id", "date_order", "line_ids"]
        )

    def test_default_get(self):
        """
        When we create record check that it
        is correctly defaulted
        """
        vals = self.ppr.default_get(
            ["name", "partner_id", "date_order", "line_ids"]
        )
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
            sum(recalc.line_ids.mapped("price_subtotal")),
            recalc.total,
            delta=1,
        )
        # We test that the pricing is roughly weighted in proportion
        approx_change = self.po.amount_untaxed / recalc.total
        subtotal = 0.0
        for l in recalc.line_ids:
            p = l.name
            self.assertAlmostEqual(
                p.price_subtotal / l.price_subtotal, approx_change, delta=1
            )
            subtotal += l.price_subtotal
        recalc.action_write()
        self.assertFalse(fc(self.po.amount_untaxed, subtotal, 2))

    def test_change_line_price(self):
        """Test the changing a subtotal works correctly"""
        line = self.env["purchase.price.recalculation.line"].new()
        line.update(
            {
                "price_unit": 20.0,
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
            self.assertFalse(
                fc(line.price_subtotal, line.price_unit * line.qty, 2)
            )
