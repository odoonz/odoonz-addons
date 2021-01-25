# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
import wdb

class TestProduct(common.TransactionCase):
    def setUp(self):
        super(TestProduct, self).setUp()
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
        # wdb.set_trace()
        # self.product_template_attribute_value_1 = self.env["product.template.attribute.value"].create(
        #     {
        #         "attribute_line_id": self.product_attribute_line_1.id,
        #         "product_attribute_value_id": self.product_attribute_value_1.id,
        #         "price_extra": 50.40,
        #     }
        # )
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
        self.raw1_product = self.env["product.product"].create(
            {
                "name": "Dishwasher - Inner Subassembly",
                "categ_id": self.env.ref("product.product_category_5").id,
                "standard_price": 500.0,
                "list_price": 1000.0,
                "type": "consu",
                "weight": 80,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "product_tmpl_id": self.manu_product_product_template.id,
            }
        )

    def test_bom_count(self):
        self.assertEqual(
            self.manu_product_product_template.used_in_bom_count, 0
        )
        self.assertEqual(
            self.raw1_product.used_in_bom_count, 1
        )

    def test_action_used_in_bom(self):
        product = self.raw1_product
        action = product.action_used_in_bom()
        self.assertIn(
            ("bom_line_ids.product_tmpl_id", "=", product.product_tmpl_id.id),
            action.get("domain", []),
        )
