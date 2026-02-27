# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestXformSubstitutionMap(TransactionCase):
    """Tests for xform.substitution.map."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_src = cls.env["product.product"].create({"name": "Source Product"})
        cls.product_dest = cls.env["product.product"].create({"name": "Dest Product"})

    def test_get_substitute_found(self):
        """_get_substitute returns dest when mapping exists."""
        self.env["xform.substitution.map"].create(
            {
                "src_product_ids": [Command.set(self.product_src.ids)],
                "dest_product_id": self.product_dest.id,
            }
        )
        result = self.env["xform.substitution.map"]._get_substitute(self.product_src)
        self.assertEqual(result, self.product_dest)

    def test_get_substitute_not_found(self):
        """_get_substitute returns original when no mapping."""
        other = self.env["product.product"].create({"name": "Unmapped Product"})
        result = self.env["xform.substitution.map"]._get_substitute(other)
        self.assertEqual(result, other)
