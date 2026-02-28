from odoo.fields import Command
from odoo.tests import tagged
from odoo.tools import float_round

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestMrpDynamic(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Simple attribute used to match finished and raw variants.
        cls.color_attribute = cls.env["product.attribute"].create(
            {
                "name": "Color (MRP Dynamic Line Tests)",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Red"}),
                    Command.create({"name": "Blue"}),
                ],
            }
        )
        cls.color_red, cls.color_blue = cls.color_attribute.value_ids

        # Finished product with color variants and a weight.
        cls.finished_tmpl = cls.env["product.template"].create(
            {
                "name": "Dynamic Dumbbell",
                "weight": 10.0,
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

        # Raw material template with the same color attribute.
        cls.raw_tmpl = cls.env["product.template"].create(
            {
                "name": "Dynamic Rubber",
                "uom_id": cls.uom_kgm.id,
                "weight": 2.0,
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

        # Variants: pick the blue ones for finished + raw, and create a
        # substitute product for the raw material.
        def _variant_with_color(tmpl, color_value):
            return tmpl.product_variant_ids.filtered(
                lambda p: color_value
                in p.product_template_attribute_value_ids.product_attribute_value_id
            )

        cls.finished_blue = _variant_with_color(cls.finished_tmpl, cls.color_blue)
        cls.raw_blue = _variant_with_color(cls.raw_tmpl, cls.color_blue)

        cls.substitute = cls.env["product.product"].create(
            {
                "name": "Dynamic Rubber (Substitute)",
                "uom_id": cls.uom_kgm.id,
                "weight": 2.0,
            }
        )

        cls.env["xform.substitution.map"].create(
            {
                "src_product_ids": [Command.set(cls.raw_blue.ids)],
                "dest_product_id": cls.substitute.id,
            }
        )

        # BoM with a single dynamic line: match_attributes + scale_weight.
        cls.dynamic_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_tmpl.id,
                "product_qty": 1.0,
                "product_uom_id": cls.uom_kgm.id,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.raw_tmpl.product_variant_ids[0].id,
                            "product_uom_id": cls.uom_kgm.id,
                            "product_qty": 1.5,
                            "xform_ids": [
                                Command.link(
                                    cls.env.ref("mrp_dynamic_line.scale_weight").id
                                ),
                                Command.link(
                                    cls.env.ref("mrp_dynamic_line.match_attributes").id
                                ),
                            ],
                        }
                    ),
                ],
            }
        )

    def test_explode_applies_match_and_scale_xforms(self):
        """explode() applies match_attributes + scale_weight_kg in sequence."""
        boms, lines = self.dynamic_bom.explode(self.finished_blue, 1.0)
        self.assertTrue(boms)
        self.assertEqual(len(lines), 1)

        bom_line, line_fields = lines[0]

        # match_attributes + substitution map should swap to the substitute.
        self.assertEqual(line_fields["product"], self.substitute)

        # scale_weight_kg should adjust qty based on parent + raw weights.
        bom = bom_line.bom_id
        parent_weight = (
            bom.product_uom_id._compute_quantity(
                bom.product_qty, self.finished_blue.uom_id
            )
            * self.finished_blue.weight
            or 1.0
        )
        weight_factor = 1 / (self.substitute.weight or 1.0)
        expected_qty = (
            parent_weight
            * line_fields["original_qty"]
            * bom_line.product_qty
            * weight_factor
        )
        expected_qty = float_round(
            expected_qty,
            precision_rounding=bom_line.product_uom_id.rounding,
            rounding_method="UP",
        )
        self.assertEqual(line_fields["qty"], expected_qty)
