# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    anglo_saxon_financial = fields.Boolean("Financial Only", default=False)
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        """
        When we add a purchase order to a manually created invoice
        we know we want anglosaxon, unless we are recharging on
        behalf of another company
        """
        purchase = self.purchase_id or self.purchase_vendor_bill_id.purchase_order_id
        if purchase and purchase.company_id == self.company_id:
            self.anglo_saxon_financial = False
        return super()._onchange_purchase_auto_complete()

    def toggle_financial(self):
        for move in self.filtered(lambda s: s.state == "draft"):
            move.anglo_saxon_financial = not move.anglo_saxon_financial
            if move.move_type in ("in_invoice", "in_refund"):
                for line in move.invoice_line_ids:
                    if line.product_id:
                        line._compute_account_id()

    def _stock_account_prepare_anglo_saxon_in_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_in_lines_vals()

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_prepare_anglo_saxon_out_lines_vals()

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super()._stock_account_anglo_saxon_reconcile_valuation(product=product)

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super()._reverse_move_vals(default_values, cancel=cancel)
        if self.env.context.get("no_move_lines"):
            move_vals.pop("line_ids", False)
            move_vals.pop("invoice_line_ids", False)
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.anglo_saxon_financial")
    def _compute_account_id(self):
        res = super()._compute_account_id()
        input_lines = self.filtered(
            lambda line: (
                line._can_use_stock_accounts()
                and line.move_id.company_id.anglo_saxon_accounting
                and line.move_id.is_purchase_document()
                and line.move_id.anglo_saxon_financial
            )
        )
        for line in input_lines:
            line = line.with_company(line.move_id.journal_id.company_id)
            fiscal_position = line.move_id.fiscal_position_id
            accounts = line.product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=fiscal_position
            )
            if accounts:
                line.account_id = accounts["expense"]
        return res

    def _eligible_for_cogs(self):
        self.ensure_one()
        if self.move_id.anglo_saxon_financial or self.env.context.get(
            "anglo_saxon_financial"
        ):
            return False
        return super()._eligible_for_cogs()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _compute_qty_invoiced(self):
        self = self.with_context(exclude_financial=True)
        return super()._compute_qty_invoiced()

    def _get_invoice_lines(self):
        invoice_lines = super()._get_invoice_lines()
        if self._context.get("exclude_financial"):
            invoice_lines = invoice_lines.filtered(
                lambda s: not s.move_id.anglo_saxon_financial
            )
        return invoice_lines


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _compute_qty_invoiced(self):
        self = self.with_context(exclude_financial=True)
        return super()._compute_qty_invoiced()

    def _get_invoice_lines(self):
        invoice_lines = super()._get_invoice_lines()
        if self._context.get("exclude_financial"):
            invoice_lines = invoice_lines.filtered(
                lambda s: not s.move_id.anglo_saxon_financial
            )
        return invoice_lines
