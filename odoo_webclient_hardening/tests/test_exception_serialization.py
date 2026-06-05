# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

from ..post_load import (
    _GENERIC_MESSAGE,
    _GENERIC_NAME,
    redact_anonymous_payload,
)


@tagged("post_install", "-at_install")
class TestRedactAnonymousPayload(TransactionCase):
    """Unit tests for the pure redaction helper (no request needed)."""

    def _serialize(self, exc):
        return http.serialize_exception(exc)

    def test_internal_error_is_genericised(self):
        try:
            raise ValueError('connection to server at "db" port 5432 failed')
        except ValueError as exc:
            data = redact_anonymous_payload(self._serialize(exc), exc)
        self.assertEqual(data["name"], _GENERIC_NAME)
        self.assertEqual(data["message"], _GENERIC_MESSAGE)
        self.assertEqual(data["debug"], "")
        self.assertEqual(data["context"], {})
        self.assertNotIn("5432", str(data))

    def test_user_error_message_preserved(self):
        try:
            raise UserError("This action is not allowed for you.")
        except UserError as exc:
            data = redact_anonymous_payload(self._serialize(exc), exc)
        self.assertEqual(data["message"], "This action is not allowed for you.")
        self.assertEqual(data["debug"], "")

    def test_http_exception_preserved(self):
        try:
            raise NotFound()
        except NotFound as exc:
            data = redact_anonymous_payload(self._serialize(exc), exc)
        self.assertNotEqual(data["name"], _GENERIC_NAME)
        self.assertEqual(data["debug"], "")


@tagged("post_install", "-at_install")
class TestExceptionSerializationHttp(HttpCase):
    def test_anonymous_call_kw_hides_traceback(self):
        # auth="user" route hit without a session -> SessionExpired/AccessError,
        # serialized without a traceback for the anonymous caller.
        resp = self.url_open(
            "/web/dataset/call_kw",
            data='{"jsonrpc":"2.0","method":"call","params":{"model":"res.users",'
            '"method":"search","args":[[]],"kwargs":{}},"id":1}',
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("error", body)
        self.assertEqual(body["error"]["data"].get("debug"), "")

    def test_authenticated_call_keeps_traceback(self):
        self.authenticate("admin", "admin")
        resp = self.url_open(
            "/web/dataset/call_kw",
            data='{"jsonrpc":"2.0","method":"call","params":{"model":"res.users",'
            '"method":"no_such_method","args":[],"kwargs":{}},"id":1}',
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("error", body)
        self.assertTrue(body["error"]["data"].get("debug"))
