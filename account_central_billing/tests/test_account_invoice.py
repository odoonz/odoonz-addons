# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common, tagged

partner_model = "odoo.addons.account_central_billing.models.res_partner.ResPartner"


@tagged("post_install", "-at_install")
class TestAccountInvoice(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner_a = cls.env["res.partner"].create(
            {"name": "CB Test Partner A", "is_company": True}
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "CB Test Partner B", "is_company": True}
        )
        cls.partner_c = cls.env["res.partner"].create(
            {"name": "CB Test Partner C", "is_company": True}
        )

    def test_get_invoice_partner(self):
        pass

    def test_check_company_constraint(self):
        """
        Test that cannot self bill
        """
        with self.assertRaises(ValidationError):
            self.env["account.move"].create(
                {
                    "partner_id": self.company.partner_id.id,
                    "move_type": "out_invoice",
                    "company_id": self.company.id,
                }
            )

    def test_invoice_create(self):
        with mock.patch(
            f"{partner_model}._get_billing_partner", autospec=True
        ) as mock_partner:
            mock_partner.return_value = self.partner_b
            invoice = self.env["account.move"].create(
                {
                    "partner_id": self.partner_a.id,
                    "move_type": "out_invoice",
                }
            )
        self.assertEqual(invoice.partner_id.id, self.partner_b.id)
        self.assertEqual(invoice.order_partner_id.id, self.partner_a.id)
        self.assertEqual(
            invoice.order_invoice_id.id, self.partner_a.commercial_partner_id.id
        )

    def test_invoice_write(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_c.id,
                "move_type": "out_invoice",
            }
        )
        with mock.patch(
            f"{partner_model}._get_billing_partner", autospec=True
        ) as mock_partner:
            mock_partner.return_value = self.partner_b
            invoice.write({"partner_id": self.partner_a.id})
        self.assertEqual(invoice.partner_id.id, self.partner_b.id)
        self.assertEqual(invoice.order_partner_id.id, self.partner_a.id)
        self.assertEqual(
            invoice.order_invoice_id.id, self.partner_a.commercial_partner_id.id
        )

    def test_invoice_create_with_own_invoice_contact_is_not_redirected(self):
        """A partner with a dedicated Invoice Address contact but no
        `invoicing_partner_id` configured has NOT opted into central
        billing - creating an invoice for it must not be treated as a
        redirect (regression: this used to wrongly overwrite
        `order_partner_id`/`order_invoice_id`, e.g. clobbering an
        intercompany mirror invoice's real customer with the vendor's own
        bare partner - see `ril_intercompany_rules`)."""
        partner_with_contact = self.env["res.partner"].create(
            {"name": "CB Test Partner With Own Invoice Contact", "is_company": True}
        )
        self.env["res.partner"].create(
            {
                "name": "CB Test Partner With Own Invoice Contact - AP",
                "parent_id": partner_with_contact.id,
                "type": "invoice",
            }
        )
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner_with_contact.id,
                "move_type": "out_invoice",
            }
        )
        self.assertEqual(invoice.partner_id, partner_with_contact)
        self.assertFalse(invoice.order_partner_id)
        self.assertFalse(invoice.order_invoice_id)

    def test_search(self):
        pass

    def test_prepare_default_reversal(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (0, 0, {"name": "Test line", "quantity": 1, "price_unit": 100.0}),
                ],
            }
        )
        invoice.action_post()
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.context_today(invoice),
                    "reason": "no reason",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        refund_fields = reversal._prepare_default_reversal(invoice)
        self.assertIn("order_partner_id", refund_fields)
        self.assertIn("order_invoice_id", refund_fields)
