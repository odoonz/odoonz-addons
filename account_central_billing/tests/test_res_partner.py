# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.exceptions import ValidationError

module = "account_central_billing"


class TestResPartnerInvoicing(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")
        self.subsidiary = self.env.ref("%s.taupo_company" % module)
        # Create an invoicing structure
        # Branch A, B, C are ultimately billed to Customer HQ
        # by the Main company. i.e. intermediate invoices from
        # other companies need to go to Main Company.
        # Customers
        self.hq = self.env.ref("%s.res_partner_hq" % module)
        self.store_a = self.env.ref("%s.res_partner_branch_a" % module)
        self.store_b = self.env.ref("%s.res_partner_branch_b" % module)
        self.contact_a = self.env.ref("%s.res_partner_a_1" % module)

        # Suppliers
        self.supplier_hq = self.env.ref("%s.res_supplier_hq" % module)
        self.branch_a = self.env.ref("%s.res_supplier_branch_a" % module)
        self.branch_b = self.env.ref("%s.res_supplier_branch_b" % module)
        self.supp_contact_a = self.env.ref("%s.res_supplier_a_2" % module)

        self.normal_partner = self.env.ref("base.res_partner_1")
        self.invoice_account = (
            self.env["account.account"]
            .search(
                [
                    (
                        "user_type_id",
                        "=",
                        self.env.ref("account.data_account_type_receivable").id,
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
    def test_get_invoicing_partner_vals(self):
        """
        Test invoicing_partner_id is returned when vals supplied
        """
        # Type is usually part of view context
        vals = dict(type="out_invoice", company_id=self.company.id)
        self.assertEqual(
            self.store_b.get_billing_partner(vals),
            self.hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.contact_a.get_billing_partner(vals),
            self.hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )

        vals = dict(type="out_invoice", company_id=self.subsidiary.id)
        self.assertEqual(
            self.hq.get_billing_partner(vals),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.store_b.get_billing_partner(vals),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.contact_a.get_billing_partner(vals),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_get_invoicing_partner_invoice(self):
        """
        Test invoicing_partner_id is returned when invoice supplied
        """

        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.normal_partner.id,
                "account_id": self.invoice_account,
                "type": "out_invoice",
                "company_id": self.company.id,
            }
        )
        vals = dict()
        self.assertEqual(
            self.store_b.get_billing_partner(vals, invoice=invoice),
            self.hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.contact_a.get_billing_partner(vals, invoice=invoice),
            self.hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )

        invoice.company_id = self.subsidiary.id

        self.assertEqual(
            self.hq.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.store_b.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.contact_a.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_get_billing_partner_vals(self):
        """
        Test billing_partner_id is returned when vals supplied
        """
        # Type is usually part of view context
        vals = dict(type="in_invoice", company_id=self.company.id)
        self.assertEqual(
            self.branch_b.get_billing_partner(vals),
            self.supplier_hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.supp_contact_a.get_billing_partner(vals),
            self.supplier_hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )

        vals = dict(type="in_invoice", company_id=self.subsidiary.id)
        self.assertEqual(
            self.supplier_hq.get_billing_partner(vals),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.branch_b.get_billing_partner(vals),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.supp_contact_a.get_billing_partner(vals),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_get_billing_partner_invoice(self):
        """
        Test billing_partner_id is returned when invoice supplied
        """
        # Type is usually part of view context
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.normal_partner.id,
                "account_id": self.invoice_account,
                "type": "in_invoice",
                "company_id": self.company.id,
            }
        )
        vals = dict()
        self.assertEqual(
            self.branch_b.get_billing_partner(vals, invoice=invoice),
            self.supplier_hq,
            "Centrally billed partners should use their invoicing partner",
        )
        self.assertEqual(
            self.supp_contact_a.get_billing_partner(vals, invoice=invoice),
            self.supplier_hq,
            "Contacts of centrally billed partners should use their "
            "invoicing partner",
        )

        invoice.company_id = self.subsidiary.id

        self.assertEqual(
            self.supplier_hq.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.branch_b.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Centrally billed partners of subsidiary should invoice main company",
        )
        self.assertEqual(
            self.supp_contact_a.get_billing_partner(vals, invoice=invoice),
            self.company.partner_id,
            "Contacts of centrally billed partners of subsidiary should "
            "invoice main company",
        )

    def test_commercial_fields(self):
        comm_fields = self.env["res.partner"]._commercial_fields()
        self.assertIn("invoicing_partner_id", comm_fields)
        self.assertIn("billing_partner_id", comm_fields)
