# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMrpSaleFields(TransactionCase):
    """Tests for mrp_sale_fields: sale_id/partner_id on production and workorder."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                mail_create_nolog=True,
                mail_no_track=True,
            )
        )
        cls.partner = cls.env["res.partner"].create({"name": "MRP Sale Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "MRP Sale Test Product",
                "type": "consu",
                "is_storable": True,
                "list_price": 10.0,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
            }
        )
        cls.picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation")], limit=1
        )

    def _create_sale_order(self):
        order_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "price_unit": 10.0,
                    }
                )
            ],
        }
        if "dispatch_method" in self.env["sale.order"]._fields:
            order_vals["dispatch_method"] = "yard"
        return self.env["sale.order"].create(order_vals)

    def test_production_sale_id_from_sale_line(self):
        """MO with sale_line_id computes sale_id from line's order."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        order = self._create_sale_order()
        order.action_confirm()
        line = order.order_line[0]
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "sale_line_id": line.id,
            }
        )
        prod.invalidate_recordset()
        self.assertEqual(prod.sale_id, order)
        self.assertEqual(prod.partner_id, self.partner)

    def test_production_sale_id_from_reference(self):
        """MO with reference_ids linking to sale computes sale_id."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        order = self._create_sale_order()
        order.action_confirm()
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 3.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        ref = self.env["stock.reference"].create(
            {"name": order.name, "sale_ids": [Command.link(order.id)]}
        )
        prod.reference_ids = [Command.link(ref.id)]
        prod.invalidate_recordset()
        self.assertIn(order, prod.sale_id)

    def test_production_no_sale_link(self):
        """MO without sale line or reference has no sale_id."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        prod.invalidate_recordset()
        self.assertFalse(prod.sale_id)
        self.assertFalse(prod.partner_id)

    def test_workorder_inherits_sale_from_production(self):
        """Workorder sale_id and partner_id come from production."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        if "mrp.workorder" not in self.env:
            self.skipTest("mrp.workorder not available")
        order = self._create_sale_order()
        order.action_confirm()
        line = order.order_line[0]
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 5.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "sale_line_id": line.id,
            }
        )
        prod.invalidate_recordset()
        workcenter = self.env["mrp.workcenter"].search([], limit=1)
        if not workcenter:
            workcenter = self.env["mrp.workcenter"].create({"name": "Test Workcenter"})
        wo = self.env["mrp.workorder"].create(
            {
                "production_id": prod.id,
                "workcenter_id": workcenter.id,
                "name": "Test WO",
                "product_uom_id": self.product.uom_id.id,
            }
        )
        wo.invalidate_recordset()
        self.assertEqual(wo.sale_id, prod.sale_id)
        self.assertEqual(wo.partner_id, self.partner)

    def test_workorder_no_sale_when_production_has_none(self):
        """Workorder without sale link on production has empty sale_id."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        if "mrp.workorder" not in self.env:
            self.skipTest("mrp.workorder not available")
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        workcenter = self.env["mrp.workcenter"].search([], limit=1)
        if not workcenter:
            workcenter = self.env["mrp.workcenter"].create(
                {"name": "Test Workcenter 2"}
            )
        wo = self.env["mrp.workorder"].create(
            {
                "production_id": prod.id,
                "workcenter_id": workcenter.id,
                "name": "Test WO 2",
                "product_uom_id": self.product.uom_id.id,
            }
        )
        wo.invalidate_recordset()
        self.assertFalse(wo.sale_id)
        self.assertFalse(wo.partner_id)

    def test_partner_id_follows_sale_order_partner(self):
        """partner_id on production matches the SO partner."""
        if not self.picking_type:
            self.skipTest("No mrp_operation picking type")
        partner2 = self.env["res.partner"].create({"name": "Other Customer"})
        order_vals = {
            "partner_id": partner2.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 2.0,
                        "price_unit": 10.0,
                    }
                )
            ],
        }
        if "dispatch_method" in self.env["sale.order"]._fields:
            order_vals["dispatch_method"] = "yard"
        order = self.env["sale.order"].create(order_vals)
        order.action_confirm()
        line = order.order_line[0]
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 2.0,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "sale_line_id": line.id,
            }
        )
        prod.invalidate_recordset()
        self.assertEqual(prod.partner_id, partner2)
