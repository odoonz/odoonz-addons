# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAttributeGroups(TransactionCase):
    def test_replace_values_with_attr_group(self):
        # First changing them
        attr_groups = self.ipod_memory_line.attr_group_ids | self.attr_group_2
        self.ipod_memory_line.attr_group_ids = attr_groups
        # Need to trigger this as usually called on the product template write
        self.product_ipod._create_variant_ids()
        self.assertTrue(
            self.product_ipod.attribute_line_ids[0].value_ids
            == self.attr_group_2.value_ids
        )
        # Then adding to them
        attr_groups |= self.attr_group_1
        self.ipod_memory_line.attr_group_ids = attr_groups
        self.product_ipod._create_variant_ids()
        self.assertTrue(
            self.product_ipod.attribute_line_ids[0].value_ids
            == (self.attr_group_2.value_ids + self.attr_group_1.value_ids)
        )

    def test_adding_values_to_attr_group(self):
        """
        Test by assigning the memory attribute group to 2 products and then
        adding a value to check that the number of variants has increased
        :return:
        """
        self.ipod_memory_line.attr_group_ids = self.attr_group_1
        self.ipad_memory_line.attr_group_ids = self.attr_group_1
        # The number of variants should be the product of attribute value_ids
        self.product_ipod._create_variant_ids()
        self.product_ipad._create_variant_ids()
        ipod_factor = len(self.product_ipod.product_variant_ids) / len(
            self.attr_group_1.value_ids
        )
        ipad_factor = len(self.product_ipad.product_variant_ids) / len(
            self.attr_group_1.value_ids
        )
        initial_length = len(self.attr_group_1.value_ids)
        self.attr_group_1.value_ids += self.browse_ref(
            "product_attribute_group.product_attribute_value_64gb"
        )
        self.assertTrue(len(self.attr_group_1.value_ids) == initial_length + 1)
        self.assertTrue(
            len(self.product_ipod.product_variant_ids)
            == len(self.attr_group_1.value_ids) * ipod_factor
        )
        self.assertTrue(
            len(self.product_ipad.product_variant_ids)
            == len(self.attr_group_1.value_ids) * ipad_factor
        )

    def test_removing_values_from_attr_group(self):
        """
        Test by assigning the memory attribute group to 2 products and then
        removing a value to check that the number of variants has decreased
        :return:
        """
        self.ipod_memory_line.attr_group_ids = self.attr_group_1
        self.ipad_memory_line.attr_group_ids = self.attr_group_1
        # The number of variants should be the product of attribute value_ids
        self.product_ipod._create_variant_ids()
        self.product_ipad._create_variant_ids()
        # ipod_factor = (len(self.product_ipod.product_variant_ids) //
        #                len(self.attr_group_1.value_ids))
        ipad_factor = len(self.product_ipad.product_variant_ids) // len(
            self.attr_group_1.value_ids
        )
        initial_length = len(self.attr_group_1.value_ids)
        self.attr_group_1.value_ids -= self.browse_ref(
            "product.product_attribute_value_1"
        )
        self.assertTrue(len(self.attr_group_1.value_ids) == initial_length - 1)
        # Remove this assertion it seems that behaviour has been changed if
        # only 1 variant left - unrelated to module
        # self.assertTrue(
        #     len(self.product_ipod.product_variant_ids) ==
        #     len(self.attr_group_1.value_ids) * ipod_factor)
        self.assertTrue(
            len(self.product_ipad.product_variant_ids)
            == len(self.attr_group_1.value_ids) * ipad_factor
        )

    def test_creation(self):
        # Test values belonging to group are added on create
        tmpl = self.env["product.template"].create(
            {
                "name": "We have attr group",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attr_group_1.attribute_id.id,
                            "attr_group_ids": [(6, 0, [self.attr_group_1.id])],
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            len(tmpl.product_variant_ids), len(self.attr_group_1.value_ids)
        )
        # Test manually added values (no attr groups) are created.
        tmpl2 = self.env["product.template"].create(
            {
                "name": "We have only values",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attr_group_1.attribute_id.id,
                            "value_ids": [(6, 0, self.attr_group_1.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            len(tmpl2.product_variant_ids), len(self.attr_group_1.value_ids)
        )
        # Test added values then removed group (no attr groups) are created.
        tmpl3 = self.env["product.template"].create(
            {
                "name": "We have only values",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attr_group_1.attribute_id.id,
                            "attr_group_ids": [],
                            "value_ids": [(6, 0, self.attr_group_1.value_ids.ids[:1])],
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(tmpl3.product_variant_ids), 1)

    def test_copy(self):
        res = self.attr_group_1.copy()
        self.assertFalse(res.name == self.attr_group_1.name)
        self.assertFalse(len(res.attribute_line_ids))

    def test_button_copy(self):
        res = self.attr_group_1.button_copy()
        self.assertTrue(res.get("type") == u"ir.actions.act_window")
        attr_recordset = self.attr_group_1 | self.attr_group_2
        with self.assertRaises(ValueError):
            attr_recordset.button_copy()

    def setUp(self):
        super().setUp()

        self.attr_group_1 = self.browse_ref(
            "product_attribute_group.product_attribute_group_1"
        )
        self.attr_group_2 = self.browse_ref(
            "product_attribute_group.product_attribute_group_2"
        )

        self.product_ipad = self.browse_ref(
            "product.product_product_4_product_template"
        )
        self.product_ipod = self.browse_ref(
            "product.product_product_11_product_template"
        )

        self.ipad_memory_line = self.browse_ref(
            "product.product_4_attribute_1_product_template_attribute_line"
        )
        self.ipod_memory_line = self.browse_ref(
            "product.product_11_attribute_1_product_template_attribute_line"
        )
