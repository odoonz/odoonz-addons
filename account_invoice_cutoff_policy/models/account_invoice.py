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
