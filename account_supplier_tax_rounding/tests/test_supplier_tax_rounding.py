# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo.addons.account.tests.test_account_supplier_invoice import \
    TestAccountSupplierInvoice


class TestSupplierTaxRounding(TestAccountSupplierInvoice):

    def setUp(self):
        super(TestSupplierTaxRounding, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.company.tax_calculation_rounding_method = 'round_globally'
        self.invoice_account = self.env['account.account'].search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_receivable').id)],
            limit=1).id
        self.invoice_line_account = self.env['account.account'].search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_expenses').id)],
            limit=1).id

    def test_supplier_invoice_round_per_line(self):
        """
        Test the line tax is rounded to 7 decimal places when rounding per line
        It is a bit nutty, as we call round when not rounding, and
        currency.round when rounding
        """
        tax = self.env['account.tax'].create({
            'name': 'Tax 10.0',
            'amount': 10.0,
            'amount_type': 'fixed',
            'type_tax_use': 'purchase',
        })
        self.env.ref('base.res_partner_2').tax_calc_method = 'round_per_line'
        with mock.patch('odoo.addons.account.models.account.round',
                        autospec=True) as mock_round:
            mock_round.return_value = 10.0
            invoice = self.env['account.invoice'].create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': self.invoice_account,
                'type': 'in_invoice',
            })

            self.env['account.invoice.line'].create({
                'product_id': self.env.ref('product.product_product_4').id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'invoice_id': invoice.id,
                'name': 'product that cost 100',
                'account_id': self.invoice_line_account,
                'invoice_line_tax_ids': [(6, 0, [tax.id])],
            })
            # Note rounding of tax isn't actually called in round per line
            # tax, but round can be elsewhere, however its precision should be
            # 2 regardless - this test could be better
            mock_round.assert_called_with(mock.ANY, 2)

    def test_supplier_invoice_round_globally(self):
        """
        Test that round is never called when round_globally is set
        """
        tax = self.env['account.tax'].create({
            'name': 'Tax 10.0',
            'amount': 10.0,
            'amount_type': 'fixed',
            'type_tax_use': 'purchase',
        })

        self.env.ref('base.res_partner_2').tax_calc_method = 'round_globally'
        with mock.patch('odoo.addons.account.models.account.round',
                        autospec=True) as mock_round:
            mock_round.return_value = 10.0
            invoice = self.env['account.invoice'].create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'account_id': self.invoice_account,
                'type': 'in_invoice',
            })

            self.env['account.invoice.line'].create({
                'product_id': self.env.ref('product.product_product_4').id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'invoice_id': invoice.id,
                'name': 'product that cost 100',
                'account_id': self.invoice_line_account,
                'invoice_line_tax_ids': [(6, 0, [tax.id])],
            })
            mock_round.assert_called_with(10.0, 7)
