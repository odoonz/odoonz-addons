# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_invoice_partner(self):
        """
        Hook method for extensibility to determine which partner should be used
        for checking the lock date
        :return: A res.partner recordset
        """
        return self.commercial_partner_id

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        """
        Extends the onchange to assign the invoice date based on the partners
        invoicing policy
        """
        date_invoice = self.date_invoice
        if date_invoice and self.type.startswith('out_'):
            self.date_invoice = self._get_invoice_partner()._get_lock_date(
                date_invoice)
        return super(
            AccountInvoice, self)._onchange_payment_term_date_invoice()
