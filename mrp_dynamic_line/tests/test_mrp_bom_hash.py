# Copyright Graeme Gellatly 2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import importlib
import inspect

from odoo.tests.common import TransactionCase

# Upstream changes may be valid but not tested,
# more of an early warning system for changed behaviour
FUNCTION_HASHES = {
    # full_import_path_to_class: { function_name: [valid_hashes] }
    "odoo.addons.mrp.models.mrp_production.MrpProduction": {
        "_update_raw_moves": ["3064542ffe52ea86b422353683547061"],
    },
}


class TestUpstreamHashes(TransactionCase):
    def test_upstream_function_hashes(self):
        """Test that upstream functions haven't changed"""
        for full_class_name, functions in FUNCTION_HASHES.items():
            module_name, class_name = full_class_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            for func_name, valid_hashes in functions.items():
                with self.subTest(class_name=full_class_name, func_name=func_name):
                    current_func = getattr(cls, func_name)
                    current_src = inspect.getsource(current_func).encode()
                    current_hash = hashlib.md5(current_src).hexdigest()
                    self.assertIn(
                        current_hash,
                        valid_hashes,
                        msg=f"Hash mismatch for {full_class_name}.{func_name}",
                    )
