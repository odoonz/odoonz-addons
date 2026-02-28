from random import randint, random

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleSubst(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        cls.productA = (
            cls.env["product.product"]
            .with_context(**context_no_mail)
            .create(
                {
                    "name": "Product A",
                    "default_code": "A001",
                    "list_price": 2,
                }
            )
        )
        cls.productB = (
            cls.env["product.product"]
            .with_context(**context_no_mail)
            .create(
                {
                    "name": "Product B",
                    "default_code": "B001",
                    "list_price": 4,
                }
            )
        )
        today = fields.Date.context_today(cls.productA)
        vals = {
            "partner_id": cls.env["res.partner"]
            .with_context(**context_no_mail)
            .create({"name": "Partcode Test"})
            .id,
            # "partner_invoice_id": cls.partner_a.id,
            # "partner_shipping_id": cls.partner_a.id,
            "date_order": today,
            "pricelist_id": cls.env["product.pricelist.item"]
            ._default_pricelist_id()
            .id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.productA.name,
                        "product_id": cls.productA.id,
                        "product_uom_qty": randint(1, 10),
                        "product_uom": cls.productA.uom_id.id,
                        "price_unit": randint(1, 100) / 2.1,
                        "discount": random() * 100.0,
                    },
                )
            ],
        }
        SaleOrder = cls.env["sale.order"].with_context(**context_no_mail)
        cls.so = SaleOrder.create(vals)
        cls.scr = (
            cls.env["sale.code.replacement"]
            .with_context(
                active_id=cls.so.id, active_ids=[cls.so.id], active_model="sale.order"
            )
            .create({})
        )

    def test_change_partcodes(self):
        self.assertNotEqual(self.productB.id, self.so.order_line[0].product_id.id)
        self.scr.from_code = "A"
        self.scr.to_code = "B"
        self.scr.keep_manual_pricing = False
        self.scr.change_products_partcode()
        self.assertEqual(self.productB.id, self.so.order_line[0].product_id.id)
        self.assertEqual(self.productB.list_price, self.so.order_line[0].price_unit)

    def test_change_partcodes_no_match(self):
        self.assertNotEqual(self.productB.id, self.so.order_line[0].product_id.id)
        self.scr.from_code = "A"
        self.scr.to_code = "C"
        self.scr.keep_manual_pricing = False
        expected_price = self.so.order_line[0].price_unit
        self.scr.change_products_partcode()
        self.assertEqual(self.productA.id, self.so.order_line[0].product_id.id)
        self.assertEqual(expected_price, self.so.order_line[0].price_unit)

    def test_change_partcodes_list_price(self):
        self.assertNotEqual(self.productB.id, self.so.order_line[0].product_id.id)
        self.so.order_line[0].technical_price_unit = self.productA.list_price
        self.so.order_line[0].price_unit = self.productA.list_price
        # When not keeping manual pricing, we expect the price unit to be
        # reset to the new product's list price.
        self.scr.keep_manual_pricing = False
        self.scr.from_code = "A"
        self.scr.to_code = "B"
        self.scr.change_products_partcode()
        self.assertEqual(self.productB.id, self.so.order_line[0].product_id.id)
        self.assertEqual(self.productB.list_price, self.so.order_line[0].price_unit)

    def test_change_partcodes_validation(self):
        self.so.action_confirm()
        with self.assertRaises(ValidationError):
            self.scr.change_products_partcode()
