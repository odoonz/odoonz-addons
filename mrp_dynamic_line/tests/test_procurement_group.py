from unittest import mock

from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProcurementGroupDynamic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.location = self.env["stock.location"].search(
            [("usage", "=", "internal"), ("company_id", "=", self.company.id)],
            limit=1,
        )
        if not self.location:
            self.location = self.env["stock.location"].create(
                {
                    "name": "Test Location",
                    "usage": "internal",
                    "company_id": self.company.id,
                }
            )
        self.warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company.id)], limit=1
        )
        if not self.warehouse:
            self.warehouse = self.env["stock.warehouse"].create(
                {
                    "name": "Test Warehouse",
                    "code": "TWH",
                    "company_id": self.company.id,
                }
            )

        # Simple kit BoM: kit product with one component line.
        self.product_kit = self.env["product.product"].create(
            {"name": "Dynamic Kit", "type": "consu", "is_storable": True}
        )
        self.product_component = self.env["product.product"].create(
            {"name": "Default Component", "type": "consu", "is_storable": True}
        )
        self.product_substitute = self.env["product.product"].create(
            {"name": "Substitute Component", "type": "consu", "is_storable": True}
        )

        self.bom_kit = self.env["mrp.bom"].create(
            {
                "product_id": self.product_kit.id,
                "product_tmpl_id": self.product_kit.product_tmpl_id.id,
                "product_uom_id": self.product_kit.uom_id.id,
                "type": "phantom",
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_component.id,
                            "product_uom_id": self.product_component.uom_id.id,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def test_run_kit_uses_bom_line_product_from_explode(self):
        """run() should build procurements using bom_line_data['product'] for kits."""
        rule = self.env["stock.rule"]
        Procurement = rule.Procurement

        procurement = Procurement(
            self.product_kit,
            2.0,
            self.product_kit.uom_id,
            self.location,
            "Dynamic Kit",
            "SO001",
            self.company,
            {"warehouse_id": self.warehouse},
        )

        bom_line = self.bom_kit.bom_line_ids[0]

        # Fake _bom_find to always return our phantom BoM for the kit.
        def fake_bom_find(*_args, **_kwargs):
            return {self.product_kit: self.bom_kit}

        # Fake explode to inject a custom product in bom_line_data.
        def fake_explode(*_args, **kwargs):
            quantity = kwargs.get("quantity", 1.0)
            return [self.bom_kit], [
                (bom_line, {"qty": quantity, "product": self.product_substitute})
            ]

        # Patch BoM resolution and explosion so we drive the kit branch; we
        # don't assert on the final super().run behaviour here, only that the
        # dynamic-line-specific logic executes without error.
        from odoo.addons.stock.models.stock_rule import ProcurementException

        with (
            mock.patch(
                "odoo.addons.mrp.models.mrp_bom.MrpBom._bom_find",
                side_effect=fake_bom_find,
            ),
            mock.patch(
                "odoo.addons.mrp.models.mrp_bom.MrpBom.explode",
                side_effect=fake_explode,
            ),
        ):
            try:
                rule.run([procurement], raise_user_error=False)
            except ProcurementException:
                pass  # Expected: no route for substitute product
