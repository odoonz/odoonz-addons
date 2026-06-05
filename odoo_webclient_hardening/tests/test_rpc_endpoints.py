# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import json

from odoo.tests import tagged
from odoo.tests.common import HttpCase

_JSONRPC_PAYLOAD = json.dumps(
    {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": "common", "method": "version", "args": []},
        "id": 1,
    }
)
_XMLRPC_PAYLOAD = (
    '<?xml version="1.0"?><methodCall>'
    "<methodName>version</methodName><params></params></methodCall>"
)


@tagged("post_install", "-at_install")
class TestRpcEndpoints(HttpCase):
    def test_xmlrpc_2_disabled(self):
        resp = self.url_open(
            "/xmlrpc/2/common",
            data=_XMLRPC_PAYLOAD,
            headers={"Content-Type": "text/xml"},
        )
        self.assertEqual(resp.status_code, 404)

    def test_xmlrpc_legacy_disabled(self):
        resp = self.url_open(
            "/xmlrpc/common",
            data=_XMLRPC_PAYLOAD,
            headers={"Content-Type": "text/xml"},
        )
        self.assertEqual(resp.status_code, 404)

    def test_version_info_does_not_fingerprint(self):
        resp = self.url_open(
            "/web/webclient/version_info",
            data='{"jsonrpc":"2.0","method":"call","params":{},"id":1}',
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        result = resp.json()["result"]
        self.assertNotIn("server_version", result)
        self.assertNotIn("server_version_info", result)
        self.assertNotIn("server_serie", result)
        self.assertEqual(result.get("protocol_version"), 1)

    def test_db_management_endpoints_disabled(self):
        # Management/mutating routes return 404 ...
        for path in (
            "/web/database/manager",
            "/web/database/create",
            "/web/database/duplicate",
            "/web/database/drop",
            "/web/database/backup",
            "/web/database/restore",
            "/web/database/change_password",
        ):
            resp = self.url_open(path, data={"master_pwd": "x"})
            self.assertEqual(resp.status_code, 404, path)

    def test_db_selector_and_list_still_work(self):
        # ... while the read-only selector and list endpoints remain available.
        selector = self.url_open("/web/database/selector")
        self.assertEqual(selector.status_code, 200)
        listing = self.url_open(
            "/web/database/list",
            data='{"jsonrpc":"2.0","method":"call","params":{},"id":1}',
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(listing.status_code, 200)
        self.assertIn("result", listing.json())

    def test_jsonrpc_disabled_by_default(self):
        # JSON-RPC always answers HTTP 200 and reports failures inside the
        # envelope, so the disabled endpoint surfaces as a 404 error payload.
        resp = self.url_open(
            "/jsonrpc",
            data=_JSONRPC_PAYLOAD,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotIn("result", body)
        self.assertEqual(body.get("error", {}).get("code"), 404)
