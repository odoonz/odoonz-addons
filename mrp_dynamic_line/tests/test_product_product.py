# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestProduct(common.TransactionCase):

    def test_bom_count(self):
        self.assertEquals(
            self.env.ref("mrp_dynamic_line.manu_product").used_in_bom_count, 0
        )
        self.assertEquals(
            self.env.ref("mrp_dynamic_line.raw1_product").used_in_bom_count, 1
        )

    def test_action_used_in_bom(self):
        product = self.env.ref("mrp_dynamic_line.raw1_product")
        action = product.action_used_in_bom()
        self.assertIn(
            ("bom_line_ids.product_tmpl_id", "=", product.product_tmpl_id.id),
            action.get("domain", []),
        )
