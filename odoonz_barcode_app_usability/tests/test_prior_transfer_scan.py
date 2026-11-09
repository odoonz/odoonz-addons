# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPriorTransferScan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.in_type = cls.warehouse.in_type_id
        cls.out_type = cls.warehouse.out_type_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Prior Transfer Scan Product",
                "is_storable": True,
                "type": "consu",
            }
        )
        cls.prior = cls._picking(cls.in_type)
        cls.later = cls._picking(cls.out_type)
        cls.prior.action_confirm()
        cls.later.action_confirm()
        cls.later.move_ids.move_orig_ids = cls.prior.move_ids

    @classmethod
    def _picking(cls, picking_type):
        src = picking_type.default_location_src_id
        dest = picking_type.default_location_dest_id
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                        },
                    )
                ],
            }
        )

    def test_operation_scan_opens_the_later_transfer(self):
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode(self.prior.name)
        )
        self.assertEqual(result["action"]["context"]["active_id"], self.later.id)

    def test_operation_scan_of_its_own_name_still_filters_by_name(self):
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode(self.later.name)
        )
        self.assertEqual(
            result["action"]["context"]["search_default_name"], self.later.name
        )

    def test_operation_scan_ignores_caps_lock_on_own_name(self):
        flipped = self.later.name.swapcase()
        self.assertNotEqual(flipped, self.later.name)
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode(flipped)
        )
        self.assertEqual(
            result["action"]["context"]["search_default_name"], self.later.name
        )

    def test_prior_transfer_scan_ignores_caps_lock(self):
        flipped = self.prior.name.swapcase()
        self.assertNotEqual(flipped, self.prior.name)
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode(flipped)
        )
        self.assertEqual(result["action"]["context"]["active_id"], self.later.id)

    def test_unknown_barcode_still_warns(self):
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode("NO-SUCH-TRANSFER")
        )
        self.assertTrue(result.get("warning"))

    def test_cancelled_later_transfer_is_not_found(self):
        self.later.action_cancel()
        found = self.env["stock.picking"]._barcode_find_by_prior_transfer(
            self.prior.name, picking_type=self.out_type
        )
        self.assertFalse(found)

    def test_several_later_transfers_open_a_list(self):
        second = self._picking(self.out_type)
        second.action_confirm()
        second.move_ids.move_orig_ids = self.prior.move_ids
        result = (
            self.env["stock.picking"]
            .with_context(active_id=self.out_type.id)
            .filter_on_barcode(self.prior.name)
        )
        self.assertEqual(
            set(result["action"]["domain"][0][2]),
            {self.later.id, second.id},
        )
