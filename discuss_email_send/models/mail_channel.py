# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailChannel(models.Model):
    _inherit = "mail.channel"

    email_send = fields.Boolean()

    def message_post(self, *, partner_ids=None, message_type="notification", **kwargs):
        if self.email_send and not partner_ids:
            partner_ids = self.channel_partner_ids.ids
            message_type = "comment"
        res = super().message_post(
            partner_ids=partner_ids, message_type=message_type, **kwargs
        )
        return res
