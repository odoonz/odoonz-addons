# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, tagged
import wdb

@tagged("post_install", "-at_install")
class TestMRPProduction(common.TransactionCase):
    def setUp(self):
        super(TestMRPProduction, self).setUp()
        self.appliance_product_attribute = self.env["product.attribute"].create(
            {
                "name": "Appliance Color",
                "create_variant": "always",
                "display_type": "color",
            }
        )
        self.product_attribute_value_1 = self.env["product.attribute.value"].create(
            {
                "name": "White",
                "attribute_id": self.appliance_product_attribute.id,
            }
        )
        self.product_attribute_value_2 = self.env["product.attribute.value"].create(
            {
                "name": "Black",
                "attribute_id": self.appliance_product_attribute.id,
            }
        )
        self.product_attribute_value_3 = self.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": self.appliance_product_attribute.id,
            }
        )
        self.product_attribute_value_4 = self.env["product.attribute.value"].create(
            {
                "name": "Matte",
                "attribute_id": self.appliance_product_attribute.id,
            }
        )
        self.thickness_product_attribute = self.env["product.attribute"].create(
            {
                "name": "Steel Gauge",
                "create_variant": "always",
                "display_type": "select",
            }
        )
        self.product_attribute_value_5 = self.env["product.attribute.value"].create(
            {
                "name": "0.40",
                "attribute_id": self.thickness_product_attribute.id,
            }
        )
        self.product_attribute_value_6 = self.env["product.attribute.value"].create(
            {
                "name": "0.55",
                "attribute_id": self.thickness_product_attribute.id,
            }
        )
        self.manu_product_product_template = self.env["product.template"].create(
            {
                "name": "Test Template",
                "categ_id": self.env.ref("product.product_category_5").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.product_attribute_line_1 = self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.manu_product_product_template.id,
                "attribute_id": self.appliance_product_attribute.id,
                "value_ids": [(6, 0, [self.product_attribute_value_1.id, self.product_attribute_value_2.id,
                                      self.product_attribute_value_3.id, self.product_attribute_value_4.id])],
            }
        )
        self.manu_product = self.env["product.product"].create(
            {
                "name": "Dishwasher",
                "categ_id": self.env.ref("product.product_category_5").id,
                "standard_price": 1000.0,
                "list_price": 1750.0,
                "type": "consu",
                "weight": 100,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "product_tmpl_id": self.manu_product_product_template.id,
            }
        )
        self.raw1_product_product_template = self.env["product.template"].create(
            {
                "name": "Test Template 2",
                "categ_id": self.env.ref("product.product_category_5").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.raw1_product = self.env["product.product"].create(
            {
                "name": "Dishwasher - Inner Subassembly",
                "categ_id": self.env.ref("product.product_category_5").id,
                "standard_price": 500.0,
                "list_price": 1000.0,
                "type": "consu",
                "weight": 80.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "product_tmpl_id": self.raw1_product_product_template.id,
            }
        )
        self.raw1_productb = self.env["product.product"].create(
            {
                "product_tmpl_id": self.raw1_product_product_template.id,
                "product_template_attribute_value_ids": [(6, 0, [self.product_attribute_value_2.id])],
            }
        )
        self.mrp_bom_manufacture = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.manu_product_product_template.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "sequence": 1,
            }
        )
        self.product_attribute_line_4 = self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.raw1_product_product_template.id,
                "attribute_id": self.appliance_product_attribute.id,
                "value_ids": [(6, 0, [self.product_attribute_value_1.id, self.product_attribute_value_2.id,
                                      self.product_attribute_value_3.id, self.product_attribute_value_4.id])],

            }
        )
        self.mrp_bom_manufacture = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.manu_product_product_template.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "sequence": 1,
            }
        )
        self.mrp_bom_manufacture_line_1 = self.env["mrp.bom.line"].create(
            {
                "product_tmpl_id": self.raw1_product_product_template.id,
                "variant_id": self.raw1_productb,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "sequence": 5,
                "bom_id": self.mrp_bom_manufacture.id,
            }
        )
    # Needs demo data for move application point

    def test_explode_integration1(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.manu_product.id,
                "product_qty": 1.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.env.ref("mrp_dynamic_line.mrp_bom_manufacture").id,
            }
        )
        # Check our order has correct products and quantities on lines
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 2)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.raw1_product
        )
        # manu_line 2 - scaled weight and selected product
        self.assertEquals(
            moves[1].product_id, self.raw2_product
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 25.0)

        production.button_plan()
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 2)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.raw1_product
        )
        # manu_line 2 - scaled weight and selected product
        self.assertEquals(
            moves[1].product_id, self.raw2_product
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 25.0)

    def test_explode_integration2(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.manu_productc.id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.mrp_bom_manufacture.id,
            }
        )
        # Check our order has correct products and quantities on lines
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 3)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.raw1_productc
        )
        # manu_line 2 - scaled weight and selected fall back product
        self.assertEquals(
            moves[1].product_id, self.raw2_productb
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)
        # manu line 3 - red dishwashers get a red knob
        self.assertEquals(
            moves[2].product_id, self.raw3_product
        )
        # Planning recalls explode so we check again
        production.button_plan()
        moves = production.move_raw_ids
        self.assertEquals(len(moves), 3)
        # manu_line 1
        self.assertEquals(
            moves[0].product_id, self.raw1_productc
        )
        # manu_line 2 - scaled weight and selected fall back product
        self.assertEquals(
            moves[1].product_id, self.raw2_productb
        )
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)
        # manu line 3 - red dishwashers get a red knob
        self.assertEquals(
            moves[2].product_id, self.raw3_product
        )

    def test_xform_errors(self):
        """
        These tests just confirms that a user error will pass without breaking
        a flow.
        """
        bom_line = self.mrp_bom_manufacture_line_1
        bom_line.xform_ids |= self.scale_weight
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {"name": "Dummy", "technical_name": "dummy", "application_point": "explode"}
        )
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {"name": "Dummy2", "technical_name": "dummy2", "application_point": "move"}
        )

        prod = self.env["mrp.production"].create(
            {
                "product_id": self.manu_productc.id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.mrp_bom_manufacture.id,
            }
        )
        self.assertTrue(bool(prod))
        prod.button_plan()

    def test_change_qty_errors(self):
        bom_line = self.mrp_bom_manufacture_line_1
        # Adding here to test the error code of _update_raw_move
        bom_line.xform_ids |= self.env["bom.line.xform"].create(
            {"name": "Dummy2", "technical_name": "dummy2", "application_point": "move"}
        )
        prod = self.env["mrp.production"].create(
            {
                "product_id": self.manu_productc.id,
                "product_qty": 2.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.mrp_bom_manufacture.id,
            }
        )
        moves = prod.move_raw_ids
        self.assertAlmostEquals(moves[1].product_uom_qty, 40.0)

        qty_chg = self.env["change.production.qty"].create(
            {"mo_id": prod.id, "product_qty": 1.0}
        )
        qty_chg.change_prod_qty()
        moves = prod.move_raw_ids
        self.assertAlmostEquals(moves[1].product_uom_qty, 20.0)
