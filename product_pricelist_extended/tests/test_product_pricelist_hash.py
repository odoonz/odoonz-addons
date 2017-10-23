# -*- coding: utf-8 -*-
# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import inspect
import hashlib
from odoo.tests.common import TransactionCase
from odoo.addons.product.models.product_pricelist import Pricelist as upstream

VALID_HASHES = ['46ddbd59a409b187c245d529cd2c9194']


class TestProductPricelistHash(TransactionCase):

    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._compute_price_rule).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_HASHES)
