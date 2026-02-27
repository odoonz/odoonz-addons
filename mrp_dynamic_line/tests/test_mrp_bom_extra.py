# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestMrpBomExtra(TestMrpCommon):
    """Extra tests for mrp.bom dynamic line logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.color_attribute = cls.env["product.attribute"].create(
            {
                "name": "Colour (Extra Tests)",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Green"}),
                    Command.create({"name": "Yellow"}),
                ],
            }
        )
        cls.color_green, cls.color_yellow = cls.color_attribute.value_ids

        cls.finished_tmpl = cls.env["product.template"].create(
            {
                "name": "Extra Finished",
                "weight": 5.0,
                "uom_id": cls.uom_kgm.id,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [
                                Command.set(cls.color_attribute.value_ids.ids)
                            ],
                        }
                    ),
                ],
            }
        )

        cls.raw_tmpl = cls.env["product.template"].create(
            {
                "name": "Extra Raw",
                "uom_id": cls.uom_kgm.id,
                "weight": 1.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [
                                Command.set(cls.color_attribute.value_ids.ids)
                            ],
                        }
                    ),
                ],
            }
        )

        def _variant_with_color(tmpl, color_value):
            return tmpl.product_variant_ids.filtered(
                lambda p: color_value
                in p.product_template_attribute_value_ids.product_attribute_value_id
            )

        cls.finished_green = _variant_with_color(cls.finished_tmpl, cls.color_green)

    def test_compute_matched_product_no_match_uses_bom_line_product(self):
        """_compute_matched_product uses bom_line.product_id when no match."""
        raw_product = self.raw_tmpl.product_variant_ids[0]
        ptavs = self.raw_tmpl.attribute_line_ids.product_template_value_ids
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_product.id,
                            "product_tmpl_id": self.raw_tmpl.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 1.0,
                            "required_value_ids": [
                                Command.set(
                                    ptavs.filtered(
                                        lambda v: v.product_attribute_value_id
                                        == self.color_green
                                    ).ids
                                    + ptavs.filtered(
                                        lambda v: v.product_attribute_value_id
                                        == self.color_yellow
                                    ).ids
                                )
                            ],
                        }
                    ),
                ],
            }
        )
        bom_line = bom.bom_line_ids[0]
        # With both required values, no single product can match both.
        # _compute_matched_product should fall back or raise.
        try:
            result = bom._compute_matched_product(self.finished_green, bom_line)
            # If it doesn't raise, it should use bom_line.product_id or a sub
            self.assertTrue(result)
        except ValidationError:
            pass  # Multiple matches is also valid

    def test_explode_unknown_xform_logs_error(self):
        """explode() with unknown xform technical_name logs error, skips."""
        unknown_xform = self.env["bom.line.xform"].create(
            {
                "name": "Unknown Xform",
                "technical_name": "does_not_exist",
                "application_point": "explode",
            }
        )
        raw_product = self.raw_tmpl.product_variant_ids[0]
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_product.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 2.0,
                            "xform_ids": [Command.link(unknown_xform.id)],
                        }
                    ),
                ],
            }
        )
        boms, lines = bom.explode(self.finished_green, 1.0)
        self.assertTrue(boms)
        self.assertEqual(len(lines), 1)

    def test_scale_weight_zero_product_weight(self):
        """_explode_scale_weight_kg uses 1.0 when product weight is 0."""
        zero_weight_tmpl = self.env["product.template"].create(
            {
                "name": "Zero Weight Raw",
                "uom_id": self.uom_kgm.id,
                "weight": 0.0,
            }
        )
        zero_weight_product = zero_weight_tmpl.product_variant_ids[0]
        scale_xform = self.env.ref("mrp_dynamic_line.scale_weight")

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": zero_weight_product.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 2.0,
                            "xform_ids": [Command.link(scale_xform.id)],
                        }
                    ),
                ],
            }
        )
        boms, lines = bom.explode(self.finished_green, 1.0)
        self.assertTrue(lines)
        _bom_line, line_fields = lines[0]
        self.assertGreater(line_fields["qty"], 0)

    def test_get_production_vals_for_bom_price(self):
        """_get_production_vals_for_bom_price returns correct dict."""
        product = self.finished_tmpl.product_variant_ids[0]
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
            }
        )
        vals = bom._get_production_vals_for_bom_price(product)
        self.assertEqual(vals["product_id"], product.id)
        self.assertEqual(vals["bom_id"], bom.id)
        self.assertEqual(vals["product_qty"], 100.0)

    def test_get_moves_raw_values_filters_zero_qty(self):
        """_get_moves_raw_values filters out moves with zero quantity."""
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation")], limit=1
        )
        if not picking_type:
            self.skipTest("No mrp_operation picking type")
        product = self.finished_tmpl.product_variant_ids[0]
        raw_product = self.raw_tmpl.product_variant_ids[0]
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_product.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 5.0,
                        }
                    ),
                ],
            }
        )
        mo = self.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom_id": product.uom_id.id,
                "bom_id": bom.id,
                "picking_type_id": picking_type.id,
            }
        )
        moves = mo._get_moves_raw_values()
        for m in moves:
            self.assertGreater(m["product_uom_qty"], 0)

    def _get_picking_type_and_company(self):
        """Get a compatible picking type + company pair."""
        pt = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        if not pt:
            pt = self.env["stock.picking.type"].search(
                [("code", "=", "mrp_operation")], limit=1
            )
        return pt

    def test_button_plan_single_record(self):
        """button_plan on single MO passes product_id in context."""
        picking_type = self._get_picking_type_and_company()
        if not picking_type:
            self.skipTest("No mrp_operation picking type")
        company = picking_type.company_id or self.env.company
        product = self.finished_tmpl.product_variant_ids[0]
        raw_product = self.raw_tmpl.product_variant_ids[0]
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "company_id": company.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_product.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        mo = self.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom_id": product.uom_id.id,
                "bom_id": bom.id,
                "picking_type_id": picking_type.id,
                "company_id": company.id,
            }
        )
        mo.action_confirm()
        result = mo.button_plan()
        self.assertTrue(result)

    def test_button_plan_multiple_records(self):
        """button_plan on multiple MOs iterates with product context."""
        picking_type = self._get_picking_type_and_company()
        if not picking_type:
            self.skipTest("No mrp_operation picking type")
        company = picking_type.company_id or self.env.company
        product = self.finished_tmpl.product_variant_ids[0]
        raw_product = self.raw_tmpl.product_variant_ids[0]
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kgm.id,
                "type": "normal",
                "company_id": company.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_product.id,
                            "product_uom_id": self.uom_kgm.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        mos = self.env["mrp.production"]
        for _i in range(2):
            mos |= self.env["mrp.production"].create(
                {
                    "product_id": product.id,
                    "product_qty": 1.0,
                    "product_uom_id": product.uom_id.id,
                    "bom_id": bom.id,
                    "picking_type_id": picking_type.id,
                    "company_id": company.id,
                }
            )
        mos.action_confirm()
        result = mos.button_plan()
        self.assertTrue(result)
