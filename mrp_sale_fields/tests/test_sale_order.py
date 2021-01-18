# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import Form, common


class TestSaleOrder(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.sale = self.env.ref("sale.sale_order_1")
        self.prod = self.env.ref("mrp.mrp_production_3")

    def test_compute_production_ids(self):
        self.assertEqual(self.sale.mrp_production_count, 0)
        new_order_form = Form(self.sale.copy())
        with new_order_form.order_line.new() as line:
            line.product_id = self.prod.product_id
        new_order = new_order_form.save()
        new_order.action_confirm()
        self.assertEqual(new_order.mrp_production_count, 1)

    def test_view_production(self):
        domain = self.sale.action_view_mrp_production().get("domain", [])
        self.assertIn(("sale_id", "=", self.sale.id), domain)

    # TODO Add test here to do full flow
    def test_sale_mrp_flow(self):
        pass
