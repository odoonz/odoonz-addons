# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestProductAssortment(TransactionCase):
    def setUp(self):
        super(TestProductAssortment, self).setUp()
        self.filter_obj = self.env["ir.filters"]
        self.product_obj = self.env["product.product"]
        self.assortment = self.filter_obj.create(
            {
                "name": "Test Product Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [],
            }
        )
        self.template_assortment = self.filter_obj.create(
            {
                "name": "Test Template Assortment",
                "model_id": "product.template",
                "is_assortment": True,
                "domain": [],
            }
        )
        self.category_assortment = self.filter_obj.create(
            {
                "name": "Test Category Assortment",
                "model_id": "product.category",
                "is_assortment": True,
                "domain": [],
            }
        )

    def test_assortment(self):
        products = self.product_obj.search([])
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertEqual(products.ids, products_filtered.ids)

        # reduce assortment to services products
        domain = [("type", "=", "service")]
        self.assortment.domain = domain

        products = self.product_obj.search(domain)
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertEqual(products.ids, products_filtered.ids)

        # include one product not in initial filter
        included_product = self.env.ref("product.product_product_7")
        self.assortment.write({"whitelist_product_ids": [(4, included_product.id)]})
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertIn(included_product.id, products_filtered.ids)

        # exclude one product not in initial filter
        excluded_product = self.env.ref("product.product_product_2")
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertIn(excluded_product.id, products_filtered.ids)
        self.assortment.write({"blacklist_product_ids": [(4, excluded_product.id)]})
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertNotIn(excluded_product.id, products_filtered.ids)

    def test_assortment_not_available_search_view(self):
        model = self.env.ref("product.model_product_product")
        filters = self.filter_obj.get_filters(model.id)
        self.assertFalse(filters)

    @mute_logger("odoo.sql_db")
    def test_create_assortment_without_context(self):
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.filter_obj.with_context(product_assortment=False).create(
                {"name": "Test Assortment No Context", "domain": []}
            )

    def test_product_assortment_view(self):
        included_product = self.env.ref("product.product_product_7")
        self.assortment.write({"whitelist_product_ids": [(4, included_product.id)]})
        res = self.assortment.show_products()
        self.assertEqual(res["domain"], [("id", "in", [included_product.id])])

    def test_record_count(self):
        products = self.product_obj.search([])
        self.assertEqual(self.assortment.record_count, len(products))

        # reduce assortment to services products
        domain = [("type", "=", "service")]
        self.assortment.domain = domain

        products = self.product_obj.search(domain)
        domain = self.assortment._get_product_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assortment.invalidate_cache()
        self.assertEqual(self.assortment.record_count, len(products_filtered))

