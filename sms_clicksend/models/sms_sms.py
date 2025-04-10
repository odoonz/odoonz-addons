# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..tools.sms_api import ClicksendSmsApi


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)

    def _get_related_object(self):
        """Return the object that the message is attached to

        May be useful for _get_from_email()"""
        mail_message = self.mail_message_id
        if mail_message and mail_message.model and mail_message.res_id:
            related_object = self.env[mail_message.model].browse(mail_message.res_id)
            if related_object.exists():
                return related_object
        return None

    def _get_from_email(self):
        """Hook method for providing an email address for SMS replies"""
        return None

    def _split_batch(self):
        if ClicksendSmsApi(self.env)._get_clicksend_sms_account():
            # Only send individual SMS
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
