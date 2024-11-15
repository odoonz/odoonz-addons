import base64

from odoo import models
from odoo.exceptions import UserError


class MailGroup(models.Model):
    _inherit = "mail.group"

    def button_convert_to_discuss(self):
        self.ensure_one()
        # This is bad: Fix
        self = self.sudo()
        # This try/except is a workaround in many migrations
        # double encoded b64 images
        try:
            self.image_128 = self.image_128
        except UserError:
            self.image_128 = base64.b64.decode(self.image_128)

        self.env["mail.channel"].create(
            {
                "name": self.name,
                "email_send": True,
                "description": self.description,
                "active": True,
                "group_public_id": self.access_group_id.id,
                "group_ids": self.access_group_id.ids,
                "image_128": self.image_128,
                "message_ids": self.mail_group_message_ids.mail_message_id.ids,
            }
        )
        self.active = False
