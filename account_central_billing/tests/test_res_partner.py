# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestResPartnerInvoicing(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.subsidiary = cls.env["res.company"].create(
            [
                {
                    "name": "Taupo",
                }
            ]
        )
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
