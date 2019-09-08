# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import inspect
import hashlib
from odoo.tests.common import TransactionCase
from odoo.addons.product.models.product_pricelist import Pricelist as upstream

# mostly compatible, only bug fixes different, except last entry which is base
# other hashes may be valid but not tested, more of an early warning system
# for changed behaviour

VALID_HASHES = ["9858823ca62ce6cf90f3017b053b1b35", "fe4430e66430efab9d79b37e18cb9b0c"]


class TestProductPricelistHash(TransactionCase):
    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._compute_price_rule).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_HASHES)
