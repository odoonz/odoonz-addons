from random import randint, random
from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo.tests import tagged
from odoo import fields
from odoo.tools import float_compare as fc
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestSaleSubst(TestSale):
    def setUp(self):
        super().setUp()
        today = fields.Date.to_string(fields.Date.context_today(self.partner))
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        p = self.env.ref("sale_partcode_substitution.product_product_1")
        self.blue_car = self.env.ref("sale_partcode_substitution.product_product_2")
        vals = {
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
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        SaleOrder = self.env["sale.order"].with_context(context_no_mail)
        self.so = SaleOrder.create(vals)
        self.scr = (
            self.env["sale.code.replacement"]
            .with_context(
                active_id=self.so.id, active_ids=[self.so.id], active_model="sale.order"
            )
            .create({})
        )

    def test_change_partcodes(self):
        self.assertNotEqual(self.blue_car.id, self.so.order_line[0].product_id.id)
        self.scr.from_code = "GRN"
        self.scr.to_code = "BLU"
        self.scr.change_products_partcode()
        self.assertEqual(self.blue_car.id, self.so.order_line[0].product_id.id)
        self.assertFalse(
            fc(self.blue_car.list_price, self.so.order_line[0].price_unit, 2)
        )

    def test_change_partcodes_validation(self):
        self.so.action_confirm()
        with self.assertRaises(ValidationError):
            self.scr.change_products_partcode()
