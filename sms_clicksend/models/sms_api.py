# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import logging

import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _set_error_detail(self, sms_id, message):
        self.env["sms.sms"].browse(sms_id).error_detail = message

    def _send_sms_with_clicksend(self, number, message, sms_id):
        if not number:
            # see odoo/addons/sms/models/sms_sms.py IAP_TO_SMS_STATE
            return "wrong_number_format"

        account = self._get_sms_account()
        configuration = clicksend_client.Configuration()
        configuration.username = account.sms_clicksend_username
        configuration.password = account.sms_clicksend_password
        sms_api = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
        sms_args = dict(
            source="odoo",
            to=number,
            body=message,
        )
        from_email = self.env["sms.sms"].sudo().browse(sms_id).get_from_email()
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
            self._set_error_details(sms_id, e)
            return "server_error"

    def _is_sent_with_clicksend(self):
        return self._get_sms_account().provider == "sms_clicksend"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_clicksend():
            # This method seem to be deprecated (no Odoo code use it)
            # Don't just loop over numbers, collect errors
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        """Send SMS using IAP in batch mode

        :param messages: list of SMS to send, structured as dict [{
            'res_id':  integer: ID of sms.sms,
            'number':  string: E164 formatted phone number,
            'content': string: content to send
        }]

        :return: return of /iap/sms/1/send controller which is a list of dict [{
            'res_id': integer: ID of sms.sms,
            'state':  string: 'insufficient_credit' or 'wrong_number_format' or 'success',
            'credit': integer: number of credits spent to send this SMS,
        }]

        :raises: normally none
        """
        if self._is_sent_with_clicksend():
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
