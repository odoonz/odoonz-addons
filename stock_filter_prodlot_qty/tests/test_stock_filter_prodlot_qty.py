# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockFilterProdlotQty(TransactionCase):
    def setUp(self):
        super(TestStockFilterProdlotQty, self).setUp()
        self.location_14 = self.env.ref("stock.stock_location_14")
        self.location_components = self.env.ref("stock.stock_location_components")
        self.lot0 = self.env.ref("stock.lot_product_product_cable_management_box_0")
        self.inventory = self.env.ref("stock.stock_inventory_icecream")
        self.inventory_line0 = self.env.ref("stock.stock_inventory_line_icecream_lot0")
        # make a new inventory adjustment line: same lot, different location and qty
        self.inventory_line2 = self.env["stock.inventory.line"].create(
            {
                "product_id": self.env.ref("stock.product_cable_management_box").id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_id": self.inventory.id,
                "product_qty": 30.0,
                "prod_lot_id": self.lot0.id,
                "location_id": self.location_components.id,
            }
        )
        self.inventory._action_start()
        self.inventory.action_validate()

    def test_no_location_id(self):
        self.assertEqual(self.lot0.product_qty, 80.0)
        self.assertEqual(len(self.lot0.search([])), self.lot0.search_count([]))

    def test_has_location_id(self):
        filtered_qty = self.lot0.with_context(
            location_id=self.location_14.id
        ).product_qty
        self.assertEqual(filtered_qty, 50.0)

        # check _search() filtered by location_components:
        # should be only one record in this test case
        filtered_res = self.lot0.with_context(
            location_id=self.location_components.id
        ).search([])
        for r in filtered_res:
            self.assertEqual(
                r.env.context.get("location_id"), self.location_components.id
            )
            if r.product_qty < 0:
                self.assertNotIn(
                    r,
                    filtered_res,
                    "Negative quantity should not be passed "
                    "by _action_done() in stock.inventory",
                )
