# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo.tests import common
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

partner_model = (
    "odoo.addons.account_invoice_cutoff_policy.models.res_partner.ResPartner"
)

spt = datetime.strptime


class TestAccountInvoice(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")

    def test_onchange_date_invoice(self):
        invoice = self.env["account.invoice"].new()
        invoice.type = "out_invoice"
        invoice.partner_id = self.partner

        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.date_invoice = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_payment_term_date_invoice()
        self.assertEqual(invoice.date_invoice, new_date)

    def test_onchange_date_invoice_in(self):
        invoice = self.env["account.invoice"].new()
        invoice.type = "in_invoice"
        invoice.partner_id = self.partner

        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.date_invoice = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_payment_term_date_invoice()
        self.assertEqual(invoice.date_invoice, orig_date)

    def test_onchange_date_invoice_refund(self):
        invoice = self.env["account.invoice"].new()
        invoice.type = "out_refund"
        invoice.partner_id = self.partner
        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.date_invoice = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_payment_term_date_invoice()
        self.assertEqual(invoice.date_invoice, new_date)
