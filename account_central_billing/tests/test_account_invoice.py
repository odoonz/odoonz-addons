# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock
from odoo.tests import common
from odoo.exceptions import ValidationError
partner_model = "odoo.addons.account_central_billing.models.res_partner.ResPartner"

class TestAccountInvoice(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")
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
        part2 = self.env.ref("base.res_partner_2")
        part3 = self.env.ref("base.res_partner_3")
        with mock.patch(
            "%s.get_billing_partner" % partner_model, autospec=True
        ) as mock_partner:
            mock_partner.return_value = part3
            invoice = self.env["account.move"].create(
                {
                    "partner_id": part2.id,
                    "move_type": "out_invoice",
                }
            )
        self.assertEqual(invoice.partner_id.id, part3.id)
        self.assertEqual(invoice.order_partner_id.id, part2.id)
        self.assertEqual(invoice.order_invoice_id.id, part2.commercial_partner_id.id)

    def test_invoice_write(self):
        part2 = self.env.ref("base.res_partner_2")
        part3 = self.env.ref("base.res_partner_3")
        part4 = self.env.ref("base.res_partner_4")
        invoice = self.env["account.move"].create(
            {
                "partner_id": part4.id,
            }
        )
        with mock.patch(
            "%s.get_billing_partner" % partner_model, autospec=True
        ) as mock_partner:
            mock_partner.return_value = part3
            invoice.write({"partner_id": part2.id})
        self.assertEqual(invoice.partner_id.id, part3.id)
        self.assertEqual(invoice.order_partner_id.id, part2.id)
        self.assertEqual(invoice.order_invoice_id.id, part2.commercial_partner_id.id)

    def test_search(self):
        pass

    def test_prepare_default_reversal(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "move_type": "out_invoice",
            }
        )
        refund_fields = self.env["account.move.reversal"]._prepare_default_reversal(invoice)
        self.assertIn("order_partner_id", refund_fields)
        self.assertIn("order_invoice_id", refund_fields)
