# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)

    def get_from_email(self):
        """Hook method for providing an email address for SMS replies"""
        return None

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_clicksend():
            # Only send individual SMS
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
