# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import inspect

from odoo.tests.common import TransactionCase

from odoo.addons.product.models.product_pricelist import Pricelist as upstream

# mostly compatible, only bug fixes different, except last entry which is base
# other hashes may be valid but not tested, more of an early warning system
# for changed behaviour

VALID_PRG_HASHES = ["fd62af198c5551e7f5aaece5d40ca202"]


class TestProductPricelistHash(TransactionCase):
    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._compute_price_rule_get_items).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_PRG_HASHES)
