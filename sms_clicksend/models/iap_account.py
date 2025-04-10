# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_clicksend", "SMS ClickSend")],
        ondelete={"sms_clicksend": "cascade"},
    )
    sms_clicksend_username = fields.Char(string="API Username")
    sms_clicksend_password = fields.Char(string="API Key")

    def _get_service_from_provider(self):
        if self.provider == "sms_clicksend":
            return "sms"
        return super()._get_service_from_provider()
