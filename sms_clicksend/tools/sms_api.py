# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import logging

import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException

from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.sms.tools.sms_api import SmsApi

_logger = logging.getLogger(__name__)


class ClicksendSmsApi(SmsApi):
    def __init__(self, env, account=None):
        super().__init__(env, account)
        self.clicksend_account = self._get_clicksend_sms_account()

    def _get_clicksend_sms_account(self):
        return self.env["iap.account"].search(
            [("provider", "=", "clicksend"), ("service_name", "=", "sms")]
        )

    def _set_error_detail(self, sms_id, message):
        self.env["sms.sms"].browse(sms_id).error_detail = message

    def _send_sms_with_clicksend(self, number, message, sms_id):
        if not number:
            # see odoo/addons/sms/models/sms_sms.py IAP_TO_SMS_STATE
            return "wrong_number_format"

        configuration = clicksend_client.Configuration()
        configuration.username = self.clicksend_account.sms_clicksend_username
        configuration.password = self.clicksend_account.sms_clicksend_password
        sms_api = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
        sms_args = dict(
            source="odoo",
            to=number,
            body=message,
        )
        from_email = self.env["sms.sms"].sudo().browse(sms_id)._get_from_email()
        if from_email:
            sms_args["from_email"] = from_email
        sms_message = SmsMessage(**sms_args)
        _logger.info(f"Sending SMS: {sms_message}")
        try:
            sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
            api_response = sms_api.sms_send_post(sms_messages)
            _logger.info(f"API response: {api_response}")
            # That actually returns a stringified Python dictionary...
            api_response = ast.literal_eval(api_response)
            if api_response["response_code"] == "SUCCESS":
                message_status = api_response["data"]["messages"][0]["status"]
                if message_status == "SUCCESS":
                    return "success"
                else:
                    self._set_error_detail(sms_id, message_status)
                    return "server_error"
            else:
                self._set_error_detail(sms_id, api_response["response_msg"])
                return "server_error"
        except ApiException as e:
            self._set_error_detail(sms_id, e)
            return "server_error"

    @api.model
    def _send_sms_batch(self, messages):
        """Send with ClickSend provider"""
        if self.clicksend_account:
            if len(messages) != 1:
                # Should never get here: _split_batch() override in sms.sms
                raise UserError(_("Batch sending is not supported with ClickSend"))
            state = self._send_sms_with_clicksend(
                # number, message, sms_id
                messages[0]["number"],
                messages[0]["content"],
                messages[0]["res_id"],
            )
            return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
