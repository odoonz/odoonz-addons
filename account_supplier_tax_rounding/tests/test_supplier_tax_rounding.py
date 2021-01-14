# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestSupplierTaxRounding(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.invoice = cls.init_invoice("in_invoice")

    def setUp(self):
        super().setUp()
        self.company = self.company_data["company"]
        self.company.tax_calculation_rounding_method = "round_globally"

    def test_supplier_invoice_round_per_line(self):
        """
        Test the line tax is rounded to 7 decimal places when rounding per line
        It is a bit nutty, as we call round when not rounding, and
        currency.round when rounding
        """
        tax = self.env["account.tax"].create(
            {
                "name": "Tax 10.0",
                "amount": 10.0,
                "amount_type": "fixed",
                "type_tax_use": "purchase",
            }
        )
        self.env.ref("base.res_partner_2").tax_calc_method = "round_per_line"
        with mock.patch(
            "odoo.addons.account.models.account.round", autospec=True
        ) as mock_round:
            mock_round.return_value = 10.0

            move_form = Form(
                self.env["account.move"].with_context(default_type="in_invoice")
            )
            move_form.partner_id = self.env.ref("base.res_partner_2")
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_4")
                line_form.quantity = 1.0
                line_form.price_unit = 100.0
                line_form.name = "product that cost 100"
                line_form.account_id = self.company_data["default_account_expense"]
                line_form.tax_ids.clear()
                line_form.tax_ids.add(tax)
            move_form.save()

            # Note rounding of tax isn't actually called in round per line
            # tax, but round can be elsewhere, however its precision should be
            # 2 regardless - this test could be better
            mock_round.assert_called_with(mock.ANY, 2)

    def test_supplier_invoice_round_globally(self):
        """
        Test that round is never called when round_globally is set
        """
        tax = self.env["account.tax"].create(
            {
                "name": "Tax 10.0",
                "amount": 10.0,
                "amount_type": "fixed",
                "type_tax_use": "purchase",
            }
        )

        self.env.ref("base.res_partner_2").tax_calc_method = "round_globally"
        with mock.patch(
            "odoo.addons.account.models.account.round", autospec=True
        ) as mock_round:
            mock_round.return_value = 10.0

            move_form = Form(
                self.env["account.move"].with_context(default_type="in_invoice")
            )
            move_form.partner_id = self.env.ref("base.res_partner_2")
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_4")
                line_form.quantity = 1.0
                line_form.price_unit = 100.0
                line_form.name = "product that cost 100"
                line_form.account_id = self.company_data["default_account_expense"]
                line_form.tax_ids.clear()
                line_form.tax_ids.add(tax)
            move_form.save()

            mock_round.assert_called_with(10.0, 7)
