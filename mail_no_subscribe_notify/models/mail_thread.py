# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        return super(
            MailThread, self.with_context(mail_auto_subscribe_no_notify=True)
        )._message_auto_subscribe(updated_values, followers_existing_policy)

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """Filter out automatically added partner_ids"""
        if partner_ids:
            new_ids = []
            for p in self.env["res.partner"].browse(partner_ids):
                if any(u.has_group("base.group_user") for u in p.user_ids):
                    new_ids.append(p.id)
            partner_ids = new_ids
        return super().message_subscribe(
            partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids
        )
