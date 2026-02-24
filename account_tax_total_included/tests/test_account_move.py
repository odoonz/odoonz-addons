# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAccountMoveTaxTotalIncluded(TransactionCase):
    """Test the account_tax_total_included module functionality"""

    def setUp(self):
        super().setUp()
        self.company = self.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_id": self.company.id,
            }
        )
        self.partner_inclusive = self.env["res.partner"].create(
            {
                "name": "Test Partner Inclusive",
                "company_id": self.company.id,
                "force_tax_total_included": True,
            }
        )
        self.parent_partner = self.env["res.partner"].create(
            {
                "name": "Parent Partner",
                "company_id": self.company.id,
                "force_tax_total_included": True,
            }
        )
        self.child_partner = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "company_id": self.company.id,
                "parent_id": self.parent_partner.id,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
            }
        )
        self.tax = self.env["account.tax"].create(
            {
                "name": "Test Tax 20%",
                "amount": 20.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "company_id": self.company.id,
            }
        )
        self.journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "code": "TEST",
                "type": "sale",
                "company_id": self.company.id,
            }
        )

    def test_partner_inheritance_on_create(self):
        """Test that invoices inherit the tax total included setting from partner on creation"""
        # Create invoice with non-inclusive partner
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify it inherits the partner setting
        self.assertFalse(invoice.force_tax_total_included)

        # Create invoice with inclusive partner
        invoice_inclusive = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_inclusive.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify it inherits the partner setting
        self.assertTrue(invoice_inclusive.force_tax_total_included)

    def test_child_partner_inheritance_on_create(self):
        """Test that invoices inherit the effective tax total included setting from child partners"""
        # Create invoice with child partner (should inherit from parent)
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.child_partner.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify it inherits the effective setting from parent
        self.assertTrue(invoice.force_tax_total_included)

    def test_partner_change_updates_invoice(self):
        """Test that changing partner updates the invoice's tax total included setting"""
        # Create invoice with non-inclusive partner
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify initial state
        self.assertFalse(invoice.force_tax_total_included)

        # Change partner to inclusive one
        invoice.write({"partner_id": self.partner_inclusive.id})

        # Verify the setting is updated
        self.assertTrue(invoice.force_tax_total_included)

    def test_prepare_product_base_line_for_taxes_computation(self):
        """Test that the special_mode is set correctly when force_tax_total_included is True"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_inclusive.id,  # Use inclusive partner
                "journal_id": self.journal.id,
                "company_id": self.company.id,
            }
        )

        line = self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "product_id": self.product.id,
                "quantity": 1,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [self.tax.id])],
            }
        )

        # Test the method
        base_line = invoice._prepare_product_base_line_for_taxes_computation(line)
        self.assertEqual(base_line["special_mode"], "total_included")

    def test_prepare_product_base_line_for_taxes_computation_no_force(self):
        """Test that the special_mode is not set when force_tax_total_included is False"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,  # Use non-inclusive partner
                "journal_id": self.journal.id,
                "company_id": self.company.id,
            }
        )

        line = self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "product_id": self.product.id,
                "quantity": 1,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [self.tax.id])],
            }
        )

        # Test the method
        base_line = invoice._prepare_product_base_line_for_taxes_computation(line)
        self.assertNotIn("special_mode", base_line)

    def test_partner_setting_change_updates_draft_invoices(self):
        """Test that changing partner setting updates existing draft invoices"""
        # Create invoice with non-inclusive partner
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify initial state
        self.assertFalse(invoice.force_tax_total_included)

        # Change partner setting to inclusive
        self.partner.force_tax_total_included = True

        # Verify invoice is updated
        self.assertTrue(invoice.force_tax_total_included)

    def test_parent_partner_setting_change_updates_child_invoices(self):
        """Test that changing parent partner setting updates child partner invoices"""
        # Create invoice with child partner
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.child_partner.id,
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, [self.tax.id])],
                        },
                    )
                ],
            }
        )

        # Verify initial state (inherits from parent)
        self.assertTrue(invoice.force_tax_total_included)

        # Change parent partner setting to non-inclusive
        self.parent_partner.force_tax_total_included = False

        # Verify child invoice is updated
        self.assertFalse(invoice.force_tax_total_included)

    def test_account_tax_prepare_base_line(self):
        """Test that account.tax properly handles the special_mode when move has force_tax_total_included"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_inclusive.id,  # Use inclusive partner
                "journal_id": self.journal.id,
                "company_id": self.company.id,
            }
        )

        line = self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "product_id": self.product.id,
                "quantity": 1,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [self.tax.id])],
            }
        )

        # Test the tax method
        kwargs = {}
        result = self.tax._prepare_base_line_for_taxes_computation(line, **kwargs)
        self.assertEqual(result["special_mode"], "total_included")
