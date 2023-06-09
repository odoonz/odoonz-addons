# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import inspect

from odoo.tests.common import TransactionCase

from odoo.addons.mrp.models.mrp_production import MrpProduction as upstream

# mostly compatible, only bug fixes different, except last entry which is base
# other hashes may be valid but not tested, more of an early warning system
# for changed behaviour

VALID_HASHES = ["55a2083cfc89ef40afe66a907921914c"]


class TestMrpHash(TransactionCase):
    def test_upstream_file_hash(self):
        """Test that copied upstream function hasn't received fixes"""
        func = inspect.getsource(upstream._update_raw_moves).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertIn(func_hash, VALID_HASHES)
