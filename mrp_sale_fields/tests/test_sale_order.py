# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestSaleOrder(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.sale = self.env.ref("sale.sale_order_1")
        self.prod1 = self.env.ref("mrp.mrp_production_1")
        self.prod2 = self.env.ref("mrp.mrp_production_2")

    def test_compute_production_ids(self):
        self.assertEqual(self.sale.production_count, 0)
        self.prod1.sale_id = self.sale
        self.prod2.sale_id = self.sale
        self.assertEqual(self.sale.production_count, 2)

    def test_view_production(self):
        domain = self.sale.action_view_production().get("domain", [])
        self.assertIn(("sale_id", "=", self.sale.id), domain)
