from odoo import fields
from odoo.tests import tagged

from odoo.addons.sale_stock.tests.test_anglo_saxon_valuation import (
    TestAngloSaxonValuation,
)


@tagged("post_install", "-at_install")
class TestAngloSaxonFinancial(TestAngloSaxonValuation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.categ_id.property_cost_method = "standard"
        cls.product.invoice_policy = "order"
        cls.product.standard_price = 10.0

    def test_financial_sale_invoice(self):
        sale_order = self._so_and_confirm_two_units()
        invoice = sale_order._create_invoices()
        invoice.anglo_saxon_financial = True
        invoice.action_post()

        # Check the resulting accounting entries
        amls = invoice.line_ids
        self.assertEqual(len(amls), 2)
        stock_out_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_stock_out"]
        )
        self.assertFalse(stock_out_aml)
        cogs_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_expense"]
        )
        self.assertFalse(cogs_aml)
        receivable_aml = amls.filtered(
            lambda aml: aml.account_id
            == self.company_data["default_account_receivable"]
        )
        self.assertEqual(receivable_aml.debit, 24)
        self.assertEqual(receivable_aml.credit, 0)
        income_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_revenue"]
        )
        self.assertEqual(income_aml.debit, 0)
        self.assertEqual(income_aml.credit, 24)

    def test_sale_price_credit(self):
        sale_order = self._so_and_confirm_two_units()
        invoice = sale_order._create_invoices()
        invoice.action_post()

        # Check invoice has stock lines
        amls = invoice.line_ids
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_stock_out"]
            )
        )
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_expense"]
            )
        )

        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.context_today(invoice),
                    "reason": "no reason",
                    "journal_id": invoice.journal_id.id,
                    "anglo_saxon_refund_type": "financial",
                }
            )
        )
        reversal = move_reversal.refund_moves()
        credit_note = self.env["account.move"].browse(reversal["res_id"])
        credit_note.invoice_line_ids.price_unit = 4.0
        credit_note.action_post()

        self.assertEqual(sale_order.order_line.qty_invoiced, 2)

        # Check credit values
        self.assertTrue(credit_note.anglo_saxon_financial)
        amls = credit_note.line_ids
        self.assertEqual(len(amls), 2)
        stock_out_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_stock_out"]
        )
        self.assertFalse(stock_out_aml)
        cogs_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_expense"]
        )
        self.assertFalse(cogs_aml)
        receivable_aml = amls.filtered(
            lambda aml: aml.account_id
            == self.company_data["default_account_receivable"]
        )
        self.assertEqual(receivable_aml.debit, 0)
        self.assertEqual(receivable_aml.credit, 8)
        income_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_revenue"]
        )
        self.assertEqual(income_aml.debit, 8)
        self.assertEqual(income_aml.credit, 0)

    def test_sale_stock_credit(self):
        sale_order = self._so_and_confirm_two_units()
        invoice = sale_order._create_invoices()
        invoice.action_post()

        # Check invoice has stock lines
        amls = invoice.line_ids
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_stock_out"]
            )
        )
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_expense"]
            )
        )

        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.context_today(invoice),
                    "reason": "no reason",
                    "journal_id": invoice.journal_id.id,
                    "anglo_saxon_refund_type": "stock",
                }
            )
        )
        reversal = move_reversal.refund_moves()
        credit_note = self.env["account.move"].browse(reversal["res_id"])
        credit_note.invoice_line_ids.quantity = 1.0
        credit_note.action_post()

        # Check sale quantities
        self.assertEqual(sale_order.order_line.qty_invoiced, 1)

        # Check credit values
        self.assertFalse(credit_note.anglo_saxon_financial)
        amls = credit_note.line_ids
        self.assertEqual(len(amls), 4)
        stock_out_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_stock_out"]
        )
        self.assertEqual(stock_out_aml.debit, 10)
        self.assertEqual(stock_out_aml.credit, 0)
        cogs_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_expense"]
        )
        self.assertEqual(cogs_aml.debit, 0)
        self.assertEqual(cogs_aml.credit, 10)
        receivable_aml = amls.filtered(
            lambda aml: aml.account_id
            == self.company_data["default_account_receivable"]
        )
        self.assertEqual(receivable_aml.debit, 0)
        self.assertEqual(receivable_aml.credit, 12)
        income_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_revenue"]
        )
        self.assertEqual(income_aml.debit, 12)
        self.assertEqual(income_aml.credit, 0)

    def test_sale_credit_and_reinvoice(self):
        sale_order = self._so_and_confirm_two_units()
        invoice = sale_order._create_invoices()
        invoice.action_post()

        # Check invoice has stock lines
        amls = invoice.line_ids
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_stock_out"]
            )
        )
        self.assertTrue(
            amls.filtered(
                lambda aml: aml.account_id
                == self.company_data["default_account_expense"]
            )
        )

        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.context_today(invoice),
                    "reason": "no reason",
                    "journal_id": invoice.journal_id.id,
                    "anglo_saxon_refund_type": "financial",
                }
            )
        )
        reversal = move_reversal.modify_moves()
        new_invoice = self.env["account.move"].browse(reversal["res_id"])
        new_invoice.invoice_line_ids.price_unit = 11.0
        new_invoice.action_post()

        # Check new invoice values
        self.assertFalse(new_invoice.anglo_saxon_financial)
        amls = new_invoice.line_ids
        self.assertEqual(len(amls), 4)
        stock_out_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_stock_out"]
        )
        self.assertEqual(stock_out_aml.debit, 0)
        self.assertEqual(stock_out_aml.credit, 20)
        cogs_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_expense"]
        )
        self.assertEqual(cogs_aml.debit, 20)
        self.assertEqual(cogs_aml.credit, 0)
        receivable_aml = amls.filtered(
            lambda aml: aml.account_id
            == self.company_data["default_account_receivable"]
        )
        self.assertEqual(receivable_aml.debit, 22)
        self.assertEqual(receivable_aml.credit, 0)
        income_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_revenue"]
        )
        self.assertEqual(income_aml.debit, 0)
        self.assertEqual(income_aml.credit, 22)

        credit_note = invoice.reversal_move_ids

        # Check Credit Note Values
        self.assertFalse(credit_note.anglo_saxon_financial)
        amls = credit_note.line_ids
        self.assertEqual(len(amls), 4)
        stock_out_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_stock_out"]
        )
        self.assertEqual(stock_out_aml.debit, 20)
        self.assertEqual(stock_out_aml.credit, 0)
        cogs_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_expense"]
        )
        self.assertEqual(cogs_aml.debit, 0)
        self.assertEqual(cogs_aml.credit, 20)
        receivable_aml = amls.filtered(
            lambda aml: aml.account_id
            == self.company_data["default_account_receivable"]
        )
        self.assertEqual(receivable_aml.debit, 0)
        self.assertEqual(receivable_aml.credit, 24)
        income_aml = amls.filtered(
            lambda aml: aml.account_id == self.company_data["default_account_revenue"]
        )
        self.assertEqual(income_aml.debit, 24)
        self.assertEqual(income_aml.credit, 0)
