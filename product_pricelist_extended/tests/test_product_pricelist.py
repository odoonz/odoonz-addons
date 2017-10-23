# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_compare
from odoo.addons.product.tests.test_product_pricelist import \
    TestProductPricelist


class TestProductPricelistItem(TestProductPricelist):
    """
    Note by inheriting TestProductPricelist we run all the tests
    of that test again with our module installed, ensuring existing
    functionality remains as expected
    """

    def setUp(self):
        super(TestProductPricelistItem, self).setUp()
        self.price_categ1 = self.env.ref(
            'product_pricelist_extended.price_categ1')
        self.extended_pricelist = self.ProductPricelist.create({
            'name': 'Extended Pricelist',
            'item_ids': [(0, 0, {
                'name': 'Default pricelist',
                'compute_price': 'formula',
                'base': 'pricelist',
                'base_pricelist_id': self.list0
            }), (0, 0, {
                'name': '10% Discount on Laptop',
                'applied_on': '1_product',
                'product_tmpl_ids': [(6, 0, [self.laptop_E5023.id])],
                'compute_price': 'formula',
                'base': 'list_price',
                'price_discount': 10
            }), (0, 0, {
                'name': '20% Discount on PC Components',
                'applied_on': '2_product_category',
                'price_categ_id': self.price_categ1.id,
                'compute_price': 'formula',
                'base': 'list_price',
                'price_discount': 20
            }), (0, 0, {
                'name': '30% Discount on some PC Components',
                'applied_on': '0_product_variant',
                'product_ids': [(6, 0, [self.custom_computer_kit.id,
                                        self.laptop_S3450.id])],
                'code_inclusion': self.custom_computer_kit.default_code[:3],
                'code_exclusion': self.laptop_S3450.default_code[1:4],
                'compute_price': 'formula',
                'base': 'list_price',
                'price_discount': 30
            })]
        })

    def test_pricelist_calculations(self):
        """Test calculation of product price based on pricelist using extended
        features"""
        context = {}
        context.update({'pricelist': self.extended_pricelist.id,
                        'quantity': 1})
        # I check sale price of Laptop.
        laptop = self.laptop_E5023.with_context(context)
        msg = "Wrong sale price: laptop E5023 should be %s instead of %s" % (
            laptop.price, (laptop.lst_price-(laptop.lst_price*0.10)))
        self.assertEqual(float_compare(
            laptop.price, (laptop.lst_price-(laptop.lst_price*0.10)),
            precision_digits=2), 0, msg)

        # I check sale price of ipad mini
        ipad_mini = self.ipad_mini.with_context(context)
        msg = "Wrong sale price: ipad_mini should be %s instead of %s" % (
            ipad_mini.price, (ipad_mini.lst_price-(ipad_mini.lst_price*0.20)))
        self.assertEqual(float_compare(
            ipad_mini.price, (ipad_mini.lst_price-(ipad_mini.lst_price*0.20)),
            precision_digits=2), 0, msg)

        # I check sale price of custom computer kit
        computer_kit = self.custom_computer_kit.with_context(context)
        msg = "Wrong sale price: computer_kit should be %s instead of %s" % (
            computer_kit.price,
            (computer_kit.lst_price-(computer_kit.lst_price*0.30)))
        self.assertEqual(float_compare(
            computer_kit.price,
            (computer_kit.lst_price-(computer_kit.lst_price*0.30)),
            precision_digits=2), 0, msg)

        # I check sale price of laptop S3450
        laptop_S3450 = self.laptop_S3450.with_context(context)
        msg = "Wrong sale price: laptop_S3450 should be %s instead of %s" % (
            laptop_S3450.price, laptop_S3450.lst_price)
        self.assertEqual(float_compare(
            laptop_S3450.price, laptop_S3450.lst_price,
            precision_digits=2), 0, msg)

    def test_pricelist_names(self):
        for item in self.extended_pricelist.item_ids:
            if item.price_categ_id:
                self.assertIn('Price Category', item.name)
            elif item.product_tmpl_ids:
                self.assertIn(item.product_tmpl_ids[0].name, item.name)
            elif item.product_ids:
                self.assertIn(item.product_ids[0].name, item.name)
            if item.code_inclusion:
                self.assertIn('contains', item.name)
            if item.code_exclusion:
                self.assertIn('excludes', item.name)
