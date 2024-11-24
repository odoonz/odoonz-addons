# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import importlib
import inspect

from odoo.tests.common import TransactionCase

# Upstream changes may be valid but not tested,
# more of an early warning system for changed behaviour
FUNCTION_HASHES = {
    "odoo.addons.mrp.models.mrp_production.MrpProduction": {
        "_update_raw_moves": "3a739954869c58e9a20034c00c935739",
    },
    "odoo.addons.mrp.models.stock_move.StockMove": {
        "write": "ebb7db855e21b11106366279d8f9b554",
    },
}


class TestUpstreamHashes(TransactionCase):
    def test_upstream_function_hashes(self):
        """Test that upstream functions haven't changed"""
        for full_class_name, functions in FUNCTION_HASHES.items():
            module_name, class_name = full_class_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            for func_name, expected_hash in functions.items():
                with self.subTest(class_name=full_class_name, func_name=func_name):
                    current_func = getattr(cls, func_name)
                    current_src = inspect.getsource(current_func).encode()
                    current_hash = hashlib.md5(current_src).hexdigest()
                    self.assertEqual(
                        current_hash,
                        expected_hash,
                        msg=f"Hash mismatch for {full_class_name}.{func_name}",
                    )
