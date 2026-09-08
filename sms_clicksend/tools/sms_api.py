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
        super().__init__(env, account=account)
        self.clicksend_account = self._get_clicksend_sms_account()

    def _get_clicksend_sms_account(self):
        return self.env["iap.account"].search(
            [("provider", "=", "sms_clicksend"), ("service_name", "=", "sms")]
        )

    def _send_sms_with_clicksend(self, number, content, sms_uuid):
        """Send SMS with ClickSend provider

        Returns state string like in upstream _send_sms_batch()
        in odoo/addons/sms/tools/sms_api.py
        """
        if not number:
            return "wrong_number_format"

        sms_sms = self.env["sms.sms"].sudo().search([("uuid", "=", sms_uuid)])[0]
        configuration = clicksend_client.Configuration()
        configuration.username = self.clicksend_account.sms_clicksend_username
        configuration.password = self.clicksend_account.sms_clicksend_password
        sms_api = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
        sms_args = dict(
            source="odoo",
            to=number,
            body=content,
        )
        from_email = sms_sms._get_from_email()
        if from_email:
            sms_args["from_email"] = from_email
        if self.clicksend_account.sms_clicksend_from:
            # Serialised as "from"; the client underscores the Python keyword
            sms_args["_from"] = self.clicksend_account.sms_clicksend_from
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
                    sms_sms.error_detail = message_status
                    return "server_error"
            else:
                sms_sms.error_detail = api_response["response_msg"]
                return "server_error"
        except ApiException as e:
            sms_sms.error_detail = e
            return "server_error"

    @api.model
    def _send_sms_batch(self, messages, delivery_reports_url=False):
        """Send with ClickSend provider"""
        if self.clicksend_account:
            if len(messages) != 1:
                # Should never get here: _split_batch() override in sms.sms
                raise UserError(_("Batch sending is not supported with ClickSend"))
            if len(messages[0]["numbers"]) != 1:
                # Same messages to multiple numbers is still batch sending
                raise UserError(_("Batch sending is not supported with ClickSend"))
            sms_uuid = messages[0]["numbers"][0]["uuid"]
            state = self._send_sms_with_clicksend(
                number=messages[0]["numbers"][0]["number"],
                content=messages[0]["content"],
                sms_uuid=sms_uuid,
            )
            return [{"state": state, "credit": 0, "uuid": sms_uuid}]
        else:
            return super()._send_sms_batch(
                messages, delivery_reports_url=delivery_reports_url
            )
