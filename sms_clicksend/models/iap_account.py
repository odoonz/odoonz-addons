# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_clicksend", "SMS ClickSend")],
        ondelete={"sms_clicksend": "cascade"},
    )
    sms_clicksend_username = fields.Char(string="API Username")
    sms_clicksend_password = fields.Char(string="API Key")

    @api.onchange("provider")
    def _onchange_provider(self):
        """ClickSend accounts are always for SMS and always registered"""
        if self.provider == "sms_clicksend":
            self.service_id = self.env["iap.service"].search(
                [("technical_name", "=", "sms")], limit=1
            )
            self.state = "registered"

    @api.model_create_multi
    def create(self, vals_list):
        """Always treat ClickSend accounts as registered"""
        for vals in vals_list:
            if vals.get("provider") == "sms_clicksend":
                vals["state"] = "registered"
        return super().create(vals_list)

    def write(self, vals):
        """Always treat ClickSend accounts as registered"""
        if vals.get("provider") == "sms_clicksend":
            vals["state"] = "registered"
        return super().write(vals)

    def _get_account_info(self, account_id, balance, information):
        """Mock account info query for ClickSend"""
        if self.provider == "sms_clicksend":
            # TODO: Query Clicksend API to get the balance
            return {
                "balance": False,
                "warning_threshold": 0.0,
                "state": "registered",
                "service_locked": True,
            }
        return super()._get_account_info(account_id, balance, information)
