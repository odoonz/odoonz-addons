from odoo.addons.mrp.tests import common
from odoo.fields import Command

class TestMrpDynamic(common.TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super(TestMrpDynamic, cls).setUpClass()
        cls.color_attribute = cls.env['product.attribute'].create({
            'name': 'Color (MRP Dynamic Line Tests)',
            'create_variant': 'always',
            'value_ids': [
                Command.create({'name': 'Red'}),
                Command.create({'name': 'Blue'}),
                Command.create({'name': 'Green'}),
            ],
        })
        (
            cls.color_attribute_red,
            cls.color_attribute_blue,
            cls.color_attribute_green,
        ) = cls.color_attribute.value_ids
        cls.hand_attribute = cls.env['product.attribute'].create({
            'name': 'Hand (MRP Dynamic Line Tests)',
            'create_variant': 'always',
            'value_ids': [
                Command.create({'name': 'Left'}),
                Command.create({'name': 'Right'}),
            ],
        })
        (
            cls.hand_attribute_left,
            cls.hand_attribute_right,
        ) = cls.hand_attribute.value_ids

        cls.finished_product1 = cls.env['product.template'].create({
            'name': 'Rubber Weights (MRP Dynamic Line Tests)',
            'weight': 10.0,
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': cls.color_attribute.id,
                    'value_ids': [Command.set(cls.color_attribute.value_ids.ids)],
                }),
                ],
        })
        cls.raw_material1 = cls.env['product.template'].create({
            'name': 'Rubber (MRP Dynamic Line Tests)',
            'uom_id': cls.uom_kgm.id,
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': cls.color_attribute.id,
                    'value_ids': [Command.set(cls.color_attribute.value_ids.ids)],
                }),
                Command.create({
                    'attribute_id': cls.hand_attribute.id,
                    'value_ids': [Command.set(cls.hand_attribute.value_ids.ids)],
                }),
            ],
        })
        cls.raw_material2 = cls.env['product.template'].create({
            'name': 'Steel (MRP Dynamic Line Tests)',
            'uom_id': cls.uom_kgm.id,
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': cls.color_attribute.id,
                    'value_ids': [Command.set(cls.color_attribute.value_ids.ids)],
                }),
            ],
        })
        cls.raw_material3 = cls.env['product.template'].create({
            'name': 'Plastic Ring (MRP Dynamic Line Tests)',
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': cls.hand_attribute.id,
                    'value_ids': [Command.set(cls.hand_attribute.value_ids.ids)],
                }),
            ],
        })
        cls.raw_material4 = cls.env['product.template'].create({
            'name': 'Sticker (MRP Dynamic Line Tests)',
        })
        cls.dynamic_bom1 = cls.env['mrp.bom'].create({
            'product_tmpl_id': cls.finished_product1.id,
            'product_qty': 1.0,
            'type': 'normal',
            'ready_to_produce': 'asap',
            'consumption': 'flexible',
            'product_uom_id': cls.dynamic_bom1.uom_id.id,
            'bom_line_ids': [
                Command.create({
                    'product_id': cls.raw_material1.product_variant_id.id,
                    'product_qty': 1.5,
                    'xform_ids': [
                        Command.link(cls.env.ref('mrp_dynamic_line.scale_weight').id),
                        Command.link(cls.env.ref('mrp_dynamic_line.match_attributes').id)],
                    'required_value_ids': [Command.set(cls.TODO)],
                }),
                Command.create({
                    'product_id': cls.raw_material2.product_variant_id.id,
                    'product_qty': 2,
                    'xform_ids': [Command.link(cls.env.ref('mrp_dynamic_line.match_attributes').id)],
                }),
                Command.create({
                    'product_id': cls.raw_material3.product_variant_id.id,
                    'product_qty': 1,
                    'required_value_ids': [Command.set(cls.TODO)],
                }),
                Command.create({
                    'product_id': cls.raw_material4.product_variant_id.id,
                    'product_qty': 1,
                }),
            ],
        })

    def test_01_explode(self):
        """ Test the explode method on a BoM with dynamic lines. """
        pass









