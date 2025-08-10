# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResPartnerTaxTotalIncluded(TransactionCase):
    """Test the res.partner tax total included functionality"""

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
        self.child_partner = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "company_id": self.company.id,
                "parent_id": self.partner.id,
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

    def test_partner_force_tax_total_included_field(self):
        """Test that the partner has the force_tax_total_included field"""
        self.assertIn("force_tax_total_included", self.partner._fields)
        self.assertFalse(self.partner.force_tax_total_included)

    def test_partner_effective_force_tax_total_included_field(self):
        """Test that the partner has the effective_force_tax_total_included field"""
        self.assertIn("effective_force_tax_total_included", self.partner._fields)
        self.assertFalse(self.partner.effective_force_tax_total_included)

    def test_partner_setting_default(self):
        """Test that new partners default to False for force_tax_total_included"""
        new_partner = self.env["res.partner"].create(
            {
                "name": "New Partner",
                "company_id": self.company.id,
            }
        )
        self.assertFalse(new_partner.force_tax_total_included)
        self.assertFalse(new_partner.effective_force_tax_total_included)

    def test_partner_setting_can_be_set(self):
        """Test that the force_tax_total_included field can be set on partners"""
        self.partner.force_tax_total_included = True
        self.assertTrue(self.partner.force_tax_total_included)
        self.assertTrue(self.partner.effective_force_tax_total_included)

        self.partner.force_tax_total_included = False
        self.assertFalse(self.partner.force_tax_total_included)
        self.assertFalse(self.partner.effective_force_tax_total_included)

    def test_child_partner_inherits_from_parent(self):
        """Test that child partners inherit the effective setting from parent"""
        # Parent is not inclusive
        self.assertFalse(self.partner.effective_force_tax_total_included)
        self.assertFalse(self.child_partner.effective_force_tax_total_included)

        # Set parent to inclusive
        self.partner.force_tax_total_included = True
        self.assertTrue(self.partner.effective_force_tax_total_included)
        self.assertTrue(self.child_partner.effective_force_tax_total_included)

        # Set parent back to non-inclusive
        self.partner.force_tax_total_included = False
        self.assertFalse(self.partner.effective_force_tax_total_included)
        self.assertFalse(self.child_partner.effective_force_tax_total_included)

    def test_child_partner_override_parent(self):
        """Test that child partners can override parent setting"""
        # Set parent to inclusive
        self.partner.force_tax_total_included = True
        self.assertTrue(self.child_partner.effective_force_tax_total_included)

        # Set child to non-inclusive (overrides parent)
        self.child_partner.force_tax_total_included = False
        self.assertFalse(self.child_partner.effective_force_tax_total_included)

        # Parent should still be inclusive
        self.assertTrue(self.partner.effective_force_tax_total_included)

    def test_partner_setting_affects_new_invoices(self):
        """Test that setting force_tax_total_included on partner affects new invoices"""
        # Set partner to inclusive
        self.partner.force_tax_total_included = True

        # Create new invoice
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

        # Verify invoice inherits the setting
        self.assertTrue(invoice.force_tax_total_included)

    def test_child_partner_setting_affects_new_invoices(self):
        """Test that child partner setting affects new invoices"""
        # Set parent to inclusive
        self.partner.force_tax_total_included = True

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

        # Verify invoice inherits the effective setting from parent
        self.assertTrue(invoice.force_tax_total_included)

    def test_partner_setting_affects_existing_draft_invoices(self):
        """Test that changing partner setting affects existing draft invoices"""
        # Create invoice first
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

        # Change partner setting
        self.partner.force_tax_total_included = True

        # Verify invoice is updated
        self.assertTrue(invoice.force_tax_total_included)

    def test_partner_setting_does_not_affect_posted_invoices(self):
        """Test that changing partner setting doesn't affect posted invoices"""
        # Create invoice first
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

        # Post the invoice
        invoice.action_post()

        # Change partner setting
        self.partner.force_tax_total_included = True

        # Verify posted invoice is not affected (should remain False)
        self.assertFalse(invoice.force_tax_total_included)
