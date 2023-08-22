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
        # NOTE: In practice this we always use this module with account_central_billing but do not want
        # the modules to depend on each other - so this is a bit hackish
        partner = self.commercial_partner_id
        if hasattr(self, "order_partner_id"):
            partner |= self.order_partner_id
        return partner

    @api.onchange("invoice_date")
    def _onchange_invoice_date(self):
        """
        Extends the onchange to assign the invoice date based on the partners
        invoicing policy
        """

        invoice_date = self.invoice_date
        if invoice_date and self.move_type.startswith("out_"):
            self.invoice_date = self._get_invoice_partner()._get_lock_date(invoice_date)
        return super()._onchange_invoice_date()

    def _get_accounting_date(self, invoice_date, has_tax):
        new_invoice_date = invoice_date
        if invoice_date and self.move_type.startswith("out_"):
            new_invoice_date = self._get_invoice_partner()._get_lock_date(invoice_date)
            self.invoice_date = new_invoice_date
        return super()._get_accounting_date(new_invoice_date, has_tax)
