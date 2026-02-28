# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleOrder(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "SPQ Test Product",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "SPQ-LOT-001",
                "product_id": cls.product.id,
            }
        )
        stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
                "location_id": stock_location.id,
                "quantity": 10.0,
            }
        )

    def test_prodlot_qty(self):
        self.lot.invalidate_recordset()
        avail_qty = f"({int(self.lot.product_qty)})"
        self.assertNotIn(avail_qty, self.lot.display_name)
        self.assertIn(avail_qty, self.lot.with_context(show_qty=True).display_name)

    def test_prodlot_quant_qty(self):
        quant = self.env["stock.quant"].search([("lot_id", "=", self.lot.id)], limit=1)
        avail_qty = f"({int(quant.quantity)})"
        self.assertNotIn(avail_qty, quant.display_name)
        self.assertIn(avail_qty, quant.with_context(show_qty=True).display_name)

    def test_no_prodlot_quant_qty(self):
        no_lot_product = self.env["product.product"].create(
            {"name": "SPQ No Lot Product", "is_storable": True}
        )
        stock_location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"].create(
            {
                "product_id": no_lot_product.id,
                "location_id": stock_location.id,
                "quantity": 5.0,
            }
        )
        quant = self.env["stock.quant"].search(
            [("product_id", "=", no_lot_product.id), ("lot_id", "=", False)], limit=1
        )
        avail_qty = f"({int(quant.quantity)})"
        self.assertNotIn(avail_qty, quant.display_name)
        self.assertNotIn(avail_qty, quant.with_context(show_qty=True).display_name)
