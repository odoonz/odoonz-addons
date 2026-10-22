# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo import Command
from odoo.tests.common import TransactionCase


class TestOrderpointQtyMultiple(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Quantity Multiple Product",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "inventory_quantity": 14.5,
            }
        ).action_apply_inventory()
        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {
                "name": "Quantity Multiple Rule",
                "product_id": cls.product.id,
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.stock_location.id,
                "product_min_qty": 15.0,
                "product_max_qty": 30.0,
            }
        )

    def test_multiple_rounds_quantity_up(self):
        self.orderpoint.qty_multiple = 10
        # 30 - 14.5 = 15.5, rounded up to a multiple of 10.
        self.assertEqual(self.orderpoint.qty_to_order, 20.0)
        self.assertEqual(self.orderpoint.replenishment_uom_id_placeholder, "10")

    def test_changing_multiple_recomputes(self):
        self.orderpoint.qty_multiple = 8
        # 15.5 rounded up to a multiple of 8.
        self.assertEqual(self.orderpoint.qty_to_order, 16.0)

    def test_zero_multiple_does_not_round(self):
        self.orderpoint.qty_multiple = 0
        self.assertEqual(self.orderpoint.qty_to_order, 15.5)
        self.assertFalse(self.orderpoint.replenishment_uom_id_placeholder)

    def test_replenishment_uom_takes_priority(self):
        pack_of_6 = self.env["uom.uom"].create(
            {
                "name": "pack of 6",
                "relative_factor": 6.0,
                "relative_uom_id": self.product.uom_id.id,
            }
        )
        self.orderpoint.write(
            {"qty_multiple": 10, "replenishment_uom_id": pack_of_6.id}
        )
        # 15.5 rounded up to a whole pack of 6, ignoring the multiple of 10.
        self.assertEqual(self.orderpoint.qty_to_order, 18.0)

    def test_multiple_is_an_unsaved_unit(self):
        self.orderpoint.qty_multiple = 10
        uom_count = self.env["uom.uom"].search_count([])
        alternative = self.orderpoint._get_replenishment_multiple_alternative(
            self.orderpoint.qty_to_order
        )
        self.assertEqual(alternative.relative_factor, 10)
        self.assertEqual(alternative.relative_uom_id, self.product.uom_id)
        self.assertFalse(alternative.id)
        self.assertEqual(self.env["uom.uom"].search_count([]), uom_count)

    def test_buy_route_uses_vendor_unit_when_multiple_is_unset(self):
        buy_route = self.warehouse.buy_pull_id.route_id
        self.product.route_ids = [Command.link(buy_route.id)]
        dozen = self.env.ref("uom.product_uom_dozen")
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "Vendor"}).id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "min_qty": 0,
                "price": 1,
                "product_uom_id": dozen.id,
            }
        )
        self.orderpoint.qty_multiple = 0
        # 15.5 rounded up to a whole dozen.
        self.assertEqual(self.orderpoint.qty_to_order, 24.0)

        self.orderpoint.qty_multiple = 10
        self.assertEqual(self.orderpoint.qty_to_order, 20.0)

    def test_negative_multiple_is_rejected(self):
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.orderpoint.qty_multiple = -1
            self.orderpoint.flush_recordset(["qty_multiple"])
