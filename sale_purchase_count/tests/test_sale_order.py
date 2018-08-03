# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestSaleOrder(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.sale = self.env.ref("sale.sale_order_1")
        self.purch1 = self.env.ref("purchase.purchase_order_1")
        self.purch2 = self.env.ref("purchase.purchase_order_2")

    def test_compute_production_ids(self):
        self.assertEqual(self.sale.purchase_count, 0)
        self.purch1.write({"origin": self.sale.name})
        self.purch2.write(
            {
                "origin": "%s-%s"
                % (self.purch2.origin or "test", self.sale.name)
            }
        )
        self.sale.invalidate_cache()
        self.assertEqual(self.sale.purchase_count, 2)

    def test_view_purchase(self):
        self.purch1.write({"origin": self.sale.name})
        action = self.sale.action_view_purchase()
        self.assertEquals(self.sale.id, action.get("res_id", 0))
        self.purch2.write(
            {
                "origin": "%s-%s"
                          % (self.purch2.origin or "test", self.sale.name)
            }
        )
        action = self.sale.action_view_purchase()
        self.assertIn("domain", action)
