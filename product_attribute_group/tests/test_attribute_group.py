# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAttributeGroups(TransactionCase):
    def setUp(self):
        super().setUp()

        self.attribute = self.env["product.attribute"].create(
            {"name": "AG Test Memory"}
        )
        self.val_8gb = self.env["product.attribute.value"].create(
            {"name": "8GB", "attribute_id": self.attribute.id}
        )
        self.val_16gb = self.env["product.attribute.value"].create(
            {"name": "16GB", "attribute_id": self.attribute.id}
        )
        self.val_32gb = self.env["product.attribute.value"].create(
            {"name": "32GB", "attribute_id": self.attribute.id}
        )
        self.val_64gb = self.env["product.attribute.value"].create(
            {"name": "64GB", "attribute_id": self.attribute.id}
        )

        self.attr_group_1 = self.env["product.attribute.group"].create(
            {
                "name": "AG Test Group Small",
                "attribute_id": self.attribute.id,
                "value_ids": [
                    Command.link(self.val_8gb.id),
                    Command.link(self.val_16gb.id),
                ],
            }
        )
        self.attr_group_2 = self.env["product.attribute.group"].create(
            {
                "name": "AG Test Group Large",
                "attribute_id": self.attribute.id,
                "value_ids": [
                    Command.link(self.val_32gb.id),
                    Command.link(self.val_64gb.id),
                ],
            }
        )

        self.product_chair = self.env["product.template"].create(
            {
                "name": "AG Test Chair",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [
                                Command.link(self.val_8gb.id),
                                Command.link(self.val_16gb.id),
                            ],
                        }
                    )
                ],
            }
        )
        self.chair_memory_line = self.product_chair.attribute_line_ids[0]

        self.colour_attr = self.env["product.attribute"].create(
            {"name": "AG Test Colour"}
        )
        self.val_red = self.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": self.colour_attr.id}
        )
        self.val_blue = self.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": self.colour_attr.id}
        )

        self.product_desk = self.env["product.template"].create(
            {
                "name": "AG Test Desk",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [
                                Command.link(self.val_8gb.id),
                                Command.link(self.val_16gb.id),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": self.colour_attr.id,
                            "value_ids": [
                                Command.link(self.val_red.id),
                                Command.link(self.val_blue.id),
                            ],
                        }
                    ),
                ],
            }
        )
        self.desk_memory_line = self.product_desk.attribute_line_ids.filtered(
            lambda line: line.attribute_id == self.attribute
        )

    def test_replace_values_with_attr_group(self):
        attr_groups = self.chair_memory_line.attr_group_ids | self.attr_group_2
        self.chair_memory_line.attr_group_ids = attr_groups
        self.product_chair._create_variant_ids()
        self.assertTrue(
            self.product_chair.attribute_line_ids[0].value_ids
            == self.attr_group_2.value_ids
        )
        attr_groups |= self.attr_group_1
        self.chair_memory_line.attr_group_ids = attr_groups
        self.product_chair._create_variant_ids()
        self.assertTrue(
            self.product_chair.attribute_line_ids[0].value_ids
            == (self.attr_group_2.value_ids + self.attr_group_1.value_ids)
        )

    def test_adding_values_to_attr_group(self):
        self.chair_memory_line.attr_group_ids = self.attr_group_1
        self.desk_memory_line.attr_group_ids = self.attr_group_1
        self.product_chair._create_variant_ids()
        self.product_desk._create_variant_ids()
        chair_len = len(self.product_chair.product_variant_ids) + 1
        desk_len = len(self.product_desk.product_variant_ids) + 2
        initial_length = len(self.attr_group_1.value_ids)
        self.attr_group_1.value_ids += self.val_32gb
        self.assertTrue(len(self.attr_group_1.value_ids) == initial_length + 1)
        self.assertTrue(len(self.product_chair.product_variant_ids) == chair_len)
        self.assertTrue(len(self.product_desk.product_variant_ids) == desk_len)

    def test_removing_values_from_attr_group(self):
        self.chair_memory_line.attr_group_ids = self.attr_group_1
        self.desk_memory_line.attr_group_ids = self.attr_group_1
        self.product_chair._create_variant_ids()
        self.product_desk._create_variant_ids()
        desk_factor = len(self.product_desk.product_variant_ids) // len(
            self.attr_group_1.value_ids
        )
        initial_length = len(self.attr_group_1.value_ids)
        self.attr_group_1.value_ids -= self.val_8gb
        self.assertTrue(len(self.attr_group_1.value_ids) == initial_length - 1)
        self.assertTrue(
            len(self.product_desk.product_variant_ids)
            == len(self.attr_group_1.value_ids) * desk_factor
        )

    def test_creation(self):
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
        tmpl3 = self.env["product.template"].create(
            {
                "name": "We have only values no group",
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
        self.assertTrue(res.get("type") == "ir.actions.act_window")
        attr_recordset = self.attr_group_1 | self.attr_group_2
        with self.assertRaises(ValueError):
            attr_recordset.button_copy()
