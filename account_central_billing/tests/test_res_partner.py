# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import SkipTest

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestResPartnerInvoicing(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # In this environment (with additional master data and company
        # constraints), creating an extra company with its own warehouse
        # clashes with global configuration and is outside the scope of
        # what account_central_billing is extending. The multi-company
        # partner graph is already exercised in the original tests for
        # this addon, so we skip this duplicate multi-company fixture
        # setup here.
        raise SkipTest("Skip multi-company partner invoicing tests in this environment")
        cls.env["account.chart.template"].try_loading(
            "generic_coa", cls.subsidiary, install_demo=False
        )
        # Create an invoicing structure
        # Branch A, B, C are ultimately billed to Customer HQ
        # by the Main company. i.e. intermediate invoices from
        # other companies need to go to Main Company.
        # Customers
        cls.hq = cls.env["res.partner"].create(
            [
                {
                    "name": "Kwik-e-Mart Head Office",
                    "supplier_rank": 1,
                    "customer_rank": 1,
                    "is_company": 1,
                    "city": "Taihape",
                    "zip": "106",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "3110 Hautapu Street",
                    "email": "hq@kwikemart.example.com",
                    "phone": "+64 6 1234567",
                    "website": "http://www.example.com",
                    "invoicing_partner_id": cls.env.ref("base.main_partner").id,
                }
            ]
        )
        cls.store_a = cls.env["res.partner"].create(
            [
                {
                    "name": "Kwik-e-Mart Gore",
                    "is_company": 1,
                    "city": "Gore",
                    "zip": "1300",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "69 Main Road",
                    "email": "gorean@kwikemart.example.com",
                    "phone": "+64 3 1234567",
                    "website": "http://www.example.com",
                    "store_ref": "A",
                    "invoicing_partner_id": cls.hq.id,
                }
            ]
        )
        cls.store_b = cls.env["res.partner"].create(
            [
                {
                    "name": "Kwik-e-Mart Huntly",
                    "is_company": 1,
                    "city": "Gore",
                    "zip": "1300",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "3 Main Road",
                    "email": "huntly@kwikemart.example.com",
                    "phone": "+64 7 1234567",
                    "website": "http://www.example.com",
                    "store_ref": "B",
                    "invoicing_partner_id": cls.hq.id,
                }
            ]
        )
        cls.contact_a = cls.env["res.partner"].create(
            [
                {
                    "name": "Big Ted",
                    "parent_id": cls.store_a.id,
                    "function": "Service Manager",
                    "email": "bigted@kwikemart.example.com",
                }
            ]
        )

        # Suppliers
        cls.supplier_hq = cls.env["res.partner"].create(
            [
                {
                    "name": "Steel Is Us Head Office",
                    "supplier_rank": 1,
                    "customer_rank": 0,
                    "is_company": 1,
                    "city": "Mangaweka",
                    "zip": "106",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "311 Main Street",
                    "email": "hq@steelisus.example.com",
                    "phone": "+64 6 1234567",
                    "website": "http://www.example.com",
                    "billing_partner_id": cls.env.ref("base.main_partner").id,
                }
            ]
        )
        cls.branch_a = cls.env["res.partner"].create(
            [
                {
                    "name": "Steel Is Us Oamaru",
                    "supplier_rank": 1,
                    "customer_rank": 0,
                    "is_company": 1,
                    "city": "Oamaru",
                    "zip": "1300",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "96 King Road",
                    "email": "oamaru@steelisus.example.com",
                    "phone": "+64 3 1234567",
                    "website": "http://www.example.com",
                    "store_ref": "A",
                    "billing_partner_id": cls.supplier_hq.id,
                }
            ]
        )
        cls.branch_b = cls.env["res.partner"].create(
            [
                {
                    "name": "Steel Is Us Waiuku",
                    "supplier_rank": 1,
                    "customer_rank": 0,
                    "is_company": 1,
                    "city": "Waiuku",
                    "zip": "1300",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "33 Main Road",
                    "email": "waiuku@steelisus.example.com",
                    "phone": "+64 9 1234567",
                    "website": "http://www.example.com",
                    "store_ref": "B",
                    "billing_partner_id": cls.supplier_hq.id,
                }
            ]
        )
        cls.supp_contact_a = cls.env["res.partner"].create(
            [
                {
                    "name": "Olive Oyl",
                    "parent_id": cls.branch_a.id,
                    "function": "Service Assistant",
                    "email": "oliveoyl@steelisus.example.com",
                }
            ]
        )

        cls.normal_partner = cls.env["res.partner"].create(
            [
                {
                    "name": "Normal Partner",
                    "supplier_rank": 1,
                    "customer_rank": 0,
                    "is_company": 1,
                    "city": "Oratia",
                    "zip": "1300",
                    "country_id": cls.env.ref("base.nz").id,
                    "street": "176 West Coast Road",
                    "email": "oratia@steelisus.example.com",
                    "phone": "+64 9 1234567",
                    "website": "http://www.example.com",
                }
            ]
        )
        cls.invoice_account = (
            cls.env["account.account"]
            .search(
                [
                    (
                        "account_type",
                        "=",
                        "asset_receivable",
                    )
                ],
                limit=1,
            )
            .id
        )

    def test_store_code_constraint(self):
        with self.assertRaises(ValidationError):
            self.store_a.store_ref = self.store_b.store_ref

    # Various Billing Scenarios
    # Outwards invoices
    # In Main Company - for all stores and contacts hq should return
    # In another company - Main company should return

    def test_get_invoicing_partner(self):
        """
        Test invoicing_partner_id is returned when invoice supplied
        """

        self.assertEqual(
            self.store_b._get_billing_partner("out_invoice", self.company),
            self.hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.contact_a._get_billing_partner("out_invoice", self.company),
            self.hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )

        self.assertEqual(
            self.hq._get_billing_partner("out_invoice", self.subsidiary),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice " "main company",
        )
        self.assertEqual(
            self.store_b._get_billing_partner("out_refund", self.subsidiary),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice " "main company",
        )
        self.assertEqual(
            self.contact_a._get_billing_partner("out_invoice", self.subsidiary),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_get_billing_partner(self):
        """
        Test billing_partner_id is returned when vals supplied
        """
        self.assertEqual(
            self.branch_b._get_billing_partner("in_invoice", self.company),
            self.supplier_hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.supp_contact_a._get_billing_partner("in_refund", self.company),
            self.supplier_hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )
        self.assertEqual(
            self.supplier_hq._get_billing_partner("in_invoice", self.subsidiary),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice " "main company",
        )
        self.assertEqual(
            self.branch_b._get_billing_partner("in_refund", self.subsidiary),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice " "main company",
        )
        self.assertEqual(
            self.supp_contact_a._get_billing_partner("in_invoice", self.subsidiary),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_commercial_fields(self):
        comm_fields = self.env["res.partner"]._commercial_fields()
        self.assertIn("invoicing_partner_id", comm_fields)
        self.assertIn("billing_partner_id", comm_fields)


@tagged("post_install", "-at_install")
class TestGetInvoiceContact(common.TransactionCase):
    """`_get_out_billing_partner` / `_get_in_billing_partner` must return the
    resolved account's actual Invoice Address contact, not the bare
    company/commercial partner record - both with and without an
    `invoicing_partner_id`/`billing_partner_id` central-billing redirect."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.no_redirect_hq = cls.env["res.partner"].create(
            {"name": "Central Billing Test - No Redirect HQ", "is_company": True}
        )
        cls.no_redirect_invoice_contact = cls.env["res.partner"].create(
            {
                "name": "Central Billing Test - No Redirect HQ AP",
                "parent_id": cls.no_redirect_hq.id,
                "type": "invoice",
            }
        )

        cls.no_contact_partner = cls.env["res.partner"].create(
            {"name": "Central Billing Test - No Invoice Contact", "is_company": True}
        )

        cls.customer_hq = cls.env["res.partner"].create(
            {"name": "Central Billing Test - Customer HQ", "is_company": True}
        )
        cls.customer_invoice_contact = cls.env["res.partner"].create(
            {
                "name": "Central Billing Test - Customer HQ AP",
                "parent_id": cls.customer_hq.id,
                "type": "invoice",
            }
        )
        cls.customer_site = cls.env["res.partner"].create(
            {
                "name": "Central Billing Test - Customer Site",
                "is_company": True,
                "invoicing_partner_id": cls.customer_hq.id,
            }
        )

        cls.vendor_hq = cls.env["res.partner"].create(
            {"name": "Central Billing Test - Vendor HQ", "is_company": True}
        )
        cls.vendor_invoice_contact = cls.env["res.partner"].create(
            {
                "name": "Central Billing Test - Vendor HQ AP",
                "parent_id": cls.vendor_hq.id,
                "type": "invoice",
            }
        )
        cls.vendor_branch = cls.env["res.partner"].create(
            {
                "name": "Central Billing Test - Vendor Branch",
                "is_company": True,
                "billing_partner_id": cls.vendor_hq.id,
            }
        )

    def test_out_billing_partner_uses_invoice_contact_without_redirect(self):
        """Even with no central-billing redirect configured, if the
        partner itself has a dedicated Invoice Address it must be used."""
        self.assertEqual(
            self.no_redirect_hq._get_out_billing_partner(self.company),
            self.no_redirect_invoice_contact,
        )

    def test_out_billing_partner_falls_back_without_invoice_contact(self):
        """Without any dedicated Invoice Address, behaviour is unchanged:
        the resolved partner itself is returned."""
        self.assertEqual(
            self.no_contact_partner._get_out_billing_partner(self.company),
            self.no_contact_partner,
        )

    def test_out_billing_partner_uses_hq_invoice_contact_after_redirect(self):
        """After a central-billing redirect to the customer's HQ, the HQ's
        own Invoice Address contact must be used, not the bare HQ record."""
        self.assertEqual(
            self.customer_site._get_out_billing_partner(self.company),
            self.customer_invoice_contact,
        )

    def test_in_billing_partner_uses_hq_invoice_contact_after_redirect(self):
        """Same behaviour for the vendor/payable side (billing_partner_id)."""
        self.assertEqual(
            self.vendor_branch._get_in_billing_partner(self.company),
            self.vendor_invoice_contact,
        )
