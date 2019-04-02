# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    @api.multi
    def _message_auto_subscribe(self, updated_values):
        return super(
            MailThread, self.with_context(mail_auto_subscribe_no_notify=True)
        )._message_auto_subscribe(updated_values)
