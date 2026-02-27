from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestMrpProductionDynamic(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Simple BoM using TestMrpCommon data:
        # product_4 built from product_1 + product_2
        cls.bom = cls.bom_1

        # Add a dummy move-level xform on one BoM line to exercise the
        # _get_move_raw_values hook and its error-logging fallback.
        xform_move = cls.env["bom.line.xform"].create(
            {
                "name": "Dummy Move Xform",
                "technical_name": "nonexistent_handler",
                "application_point": "move",
            }
        )
        cls.bom.bom_line_ids[0].xform_ids = [Command.link(xform_move.id)]

    def test_get_move_raw_values_with_move_xform_does_not_crash(self):
        """_get_move_raw_values should survive unknown move xforms and delegate."""
        mo, bom, product, rm1, rm2 = self.generate_mo()
        bom_line = bom.bom_line_ids[0]
        # Pass the product record to be compatible with other overrides.
        vals = mo._get_move_raw_values(
            rm1,
            2.0,
            rm1.uom_id,
            operation_id=False,
            bom_line=bom_line,
        )
        # Basic sanity check: result contains the expected keys and a non-zero qty.
        self.assertIn("product_uom_qty", vals)
        self.assertGreater(vals["product_uom_qty"], 0)

    def test_update_raw_moves_scales_quantities_without_move_xforms(self):
        """_update_raw_moves should scale raw moves when no move xforms are defined."""
        # Use a fresh MO whose BoM lines have no move-level xforms.
        mo, bom, product, rm1, rm2 = self.generate_mo()
        # Ensure there are no move xforms on this BoM.
        bom.bom_line_ids.write({"xform_ids": [Command.clear()]})

        moves = mo.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        ).sorted("id")
        old_qtys = {move.id: move.product_uom_qty for move in moves}

        factor = 2.0
        info = mo._update_raw_moves(factor)

        # All existing moves should be updated, and their qty doubled.
        updated_ids = {m.id for m, _old, _new in info}
        self.assertTrue(updated_ids.issuperset(old_qtys.keys()))
        for move in moves:
            self.assertEqual(move.product_uom_qty, old_qtys[move.id] * factor)

    # Note: multi-record button_plan behaviour is exercised indirectly in core
    # mrp tests; we rely on those to avoid recursion issues with other addons.
