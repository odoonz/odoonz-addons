# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestSaleOrder(common.TransactionCase):

    def test_prodlot_qty(self):
        lot = self.env.ref("stock.lot_product_cable_management")
        avail_qty = "(%.0f)" % lot.product_qty
        self.assertNotIn(avail_qty, lot.name_get()[0])
        self.assertIn(
            avail_qty, lot.with_context(show_qty=True).name_get()[0][1]
        )
