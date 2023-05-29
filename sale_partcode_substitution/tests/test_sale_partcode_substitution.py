from random import randint, random

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools import float_compare as fc

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestSaleSubst(TestSaleCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        today = fields.Date.to_string(fields.Date.context_today(cls.partner_a))
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        p = cls.env.ref("sale_partcode_substitution.product_product_1")
        cls.blue_car = cls.env.ref("sale_partcode_substitution.product_product_2")
        vals = {
            "partner_id": cls.partner_a.id,
            "partner_invoice_id": cls.partner_a.id,
            "partner_shipping_id": cls.partner_a.id,
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
            "pricelist_id": cls.env.ref("product.list0").id,
        }
        SaleOrder = cls.env["sale.order"].with_context(context_no_mail)
        cls.so = SaleOrder.create(vals)
        cls.scr = (
            cls.env["sale.code.replacement"]
            .with_context(
                active_id=cls.so.id, active_ids=[cls.so.id], active_model="sale.order"
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
