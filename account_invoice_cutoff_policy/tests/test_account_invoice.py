# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from unittest import mock

from odoo.tests import common
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

partner_model = (
    "odoo.addons.account_invoice_cutoff_policy.models.res_partner.ResPartner"
)

spt = datetime.strptime

class TestAccountInvoice(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def test_onchange_invoice_date(self):
        invoice = self.env["account.move"].new()
        invoice.move_type = "out_invoice"
        invoice.partner_id = self.partner

        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.invoice_date = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_invoice_date()
        self.assertEqual(invoice.invoice_date, new_date)

    def test_onchange_invoice_date_in(self):
        invoice = self.env["account.move"].new()
        invoice.move_type = "in_invoice"
        invoice.partner_id = self.partner

        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.invoice_date = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_invoice_date()
        self.assertEqual(invoice.invoice_date, orig_date)

    def test_onchange_invoice_date_refund(self):
        invoice = self.env["account.move"].new()
        invoice.move_type = "out_refund"
        invoice.partner_id = self.partner
        orig_date = spt("2008-08-03", DEFAULT_SERVER_DATE_FORMAT).date()
        new_date = spt("2012-12-24", DEFAULT_SERVER_DATE_FORMAT).date()
        invoice.invoice_date = orig_date
        with mock.patch(
            "%s._get_lock_date" % partner_model, autospec=True
        ) as mock_date:
            mock_date.return_value = new_date
            invoice._onchange_invoice_date()
        self.assertEqual(invoice.invoice_date, new_date)
