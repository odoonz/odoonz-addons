# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_invoice_partner(self):
        """
        Hook method for extensibility to determine which partner should be used
        for checking the lock date
        :return: A res.partner recordset
        """
        return self.commercial_partner_id

    @api.depends("invoice_date", "company_id")
    def _compute_date(self):
        """
        Extends the onchange to assign the invoice date based on the partners
        invoicing policy
        """
        for invoice in self:
            invoice_date = invoice.invoice_date
            if invoice_date and invoice.move_type.startswith("out_"):
                invoice.invoice_date = invoice._get_invoice_partner()._get_lock_date(
                    invoice_date
                )
                invoice.date = invoice.invoice_date
        return super()._compute_date()

    @api.constrains("invoice_date", "date")
    def _check_invoice_date(self):
        for inv in self:
            if inv.date and inv.invoice_date and inv.date > inv.invoice_date:
                inv.invoice_date = inv.date
