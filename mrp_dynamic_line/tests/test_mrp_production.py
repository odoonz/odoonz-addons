# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestMRPProduction(common.TransactionCase):

    def setUp(self):
        super(TestMRPProduction, self).setUp()

    # Needs demo data for move application point

    def test_explode_integration1(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref("mrp_dynamic_line.manu_product").id,
                "product_qty": 1.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.env.ref(
                    "mrp_dynamic_line.mrp_bom_manufacture"
                ).id,
            }
        )
        # Check our order has correct products and quantities on lines
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 2)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.env.ref("mrp_dynamic_line.raw1_product")
        )
        # manu_line 2 - scaled weight and selected product
        self.assertEquals(
            moves[1].product_id, self.env.ref("mrp_dynamic_line.raw2_product")
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 25.0)

        production.button_plan()
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 2)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.env.ref("mrp_dynamic_line.raw1_product")
        )
        # manu_line 2 - scaled weight and selected product
        self.assertEquals(
            moves[1].product_id, self.env.ref("mrp_dynamic_line.raw2_product")
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 25.0)

    def test_explode_integration2(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref(
                    "mrp_dynamic_line.manu_productc"
                ).id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.env.ref(
                    "mrp_dynamic_line.mrp_bom_manufacture"
                ).id,
            }
        )
        # Check our order has correct products and quantities on lines
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 3)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.env.ref("mrp_dynamic_line.raw1_productc")
        )
        # manu_line 2 - scaled weight and selected fall back product
        self.assertEquals(
            moves[1].product_id, self.env.ref("mrp_dynamic_line.raw2_productb")
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)
        # manu line 3 - red dishwashers get a red knob
        self.assertEquals(
            moves[2].product_id, self.env.ref("mrp_dynamic_line.raw3_product")
        )
        # Planning recalls explode so we check again
        production.button_plan()
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 3)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.env.ref("mrp_dynamic_line.raw1_productc")
        )
        # manu_line 2 - scaled weight and selected fall back product
        self.assertEquals(
            moves[1].product_id, self.env.ref("mrp_dynamic_line.raw2_productb")
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)
        # manu line 3 - red dishwashers get a red knob
        self.assertEquals(
            moves[2].product_id, self.env.ref("mrp_dynamic_line.raw3_product")
        )

    def test_xform_errors(self):
        """
        These tests just confirms that a user error will pass without breaking
        a flow.
        """
        bom_line = self.env.ref("mrp_dynamic_line.mrp_bom_manufacture_line_1")
        bom_line.xform_ids |= self.env.ref("mrp_dynamic_line.scale_weight")
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {'name': 'Dummy',
             'technical_name': 'dummy',
             'application_point': 'explode'}
        )
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {'name': 'Dummy2',
             'technical_name': 'dummy2',
             'application_point': 'move'}
        )

        prod = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref(
                    "mrp_dynamic_line.manu_productc"
                ).id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.env.ref(
                    "mrp_dynamic_line.mrp_bom_manufacture"
                ).id,
            }
        )
        self.assertTrue(bool(prod))
        prod.button_plan()

    def test_change_qty_errors(self):
        bom_line = self.env.ref("mrp_dynamic_line.mrp_bom_manufacture_line_1")
        # Adding here to test the error code of _update_raw_move
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {'name': 'Dummy2',
             'technical_name': 'dummy2',
             'application_point': 'move'}
        )
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref(
                    "mrp_dynamic_line.manu_productc"
                ).id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.env.ref(
                    "mrp_dynamic_line.mrp_bom_manufacture"
                ).id,
            }
        )
        moves = prod.move_raw_ids
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)

        qty_chg = self.env["change.production.qty"].create({
            "mo_id": prod.id,
            "product_qty": 1.0,
        })
        qty_chg.change_prod_qty()
        moves = prod.move_raw_ids
        self.assertAlmostEquals(moves[1].product_uom_qty, 20.0)
