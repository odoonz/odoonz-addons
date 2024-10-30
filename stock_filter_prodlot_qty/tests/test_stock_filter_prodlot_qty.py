# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.test_stock_lot import TestLotSerial


class TestStockFilterLotQty(TestLotSerial):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockQuantObj.create(
            {
                "product_id": cls.productA.id,
                "location_id": cls.locationB.id,
                "quantity": 50.0,
                "lot_id": cls.lot_p_a.id,
            }
        )
        # cls.location_14 = cls.env.ref("stock.stock_location_14")
        # cls.location_components = cls.env.ref("stock.stock_location_components")
        # cls.test_product = cls.env["product.product"].create({
        #     "name": "Test Tracked Product 1",
        #     "tracking": "lot",
        #     "detailed_type": "storable",
        # })
        # cls.lot0 = cls.env.ref("stock.lot_product_product_cable_management_box_0")
        # cls.inventory = cls.env.ref("stock.stock_inventory_icecream")
        # cls.inventory_line0 = cls.env.ref("stock.stock_inventory_line_icecream_lot0")
        # # make a new inventory adjustment line: same lot, different location and qty
        # cls.inventory_line2 = cls.env["stock.inventory.line"].create(
        #     {
        #         "product_id": cls.env.ref("stock.product_cable_management_box").id,
        #         "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
        #         "inventory_id": cls.inventory.id,
        #         "product_qty": 30.0,
        #         "lot_id": cls.lot0.id,
        #         "location_id": cls.location_components.id,
        #     }
        # )
        # cls.inventory._action_start()
        # cls.inventory.action_validate()

    def test_no_location_id(self):
        self.assertEqual(self.lot_p_a.product_qty, 60.0)
        self.assertEqual(len(self.lot_p_a.search([])), self.lot_p_a.search_count([]))

    def test_has_location_id(self):
        filtered_qty = self.lot_p_a.with_context(
            location_id=self.locationB.id
        ).product_qty
        self.assertEqual(filtered_qty, 50.0)

        # check _search() filtered by location_components:
        # should be only one record in this test case
        filtered_res = self.lot_p_a.with_context(location_id=self.locationC.id).search(
            [("id", "=", self.lot_p_a.id)]
        )
        self.assertFalse(filtered_res)
