# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleOrder(common.TransactionCase):
    def test_prodlot_qty(self):
        lot = self.env.ref("stock.lot_product_cable_management")
        avail_qty = f"({int(lot.product_qty)})"
        self.assertNotIn(avail_qty, lot.display_name)
        self.assertIn(avail_qty, lot.with_context(show_qty=True).display_name)

    def test_prodlot_quant_qty(self):
        quant = self.env["stock.quant"].search([("lot_id", "!=", False)], limit=1)
        avail_qty = f"({int(quant.quantity)})"
        self.assertNotIn(avail_qty, quant.display_name)
        self.assertIn(avail_qty, quant.with_context(show_qty=True).display_name)

    def test_no_prodlot_quant_qty(self):
        quant = self.env["stock.quant"].search([("lot_id", "=", False)], limit=1)
        avail_qty = f"({int(quant.quantity)})"
        self.assertNotIn(avail_qty, quant.display_name)
        self.assertNotIn(avail_qty, quant.with_context(show_qty=True).display_name)
