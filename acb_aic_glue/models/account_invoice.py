# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    """inherits account.move and adds _get_invoice_partner function"""

    _inherit = "account.move"

    def _get_invoice_partner(self):
        """
        Hook method for extensibility to determine which partner should be used
        for checking the lock date
        :return: A res.partner recordset
        """
        return super()._get_invoice_partner() + self.order_partner_id
