# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase


@tagged("post_install", "-at_install")
class TestResetPasswordModel(TransactionCase):
    def test_unknown_login_is_silent_no_op(self):
        # Core raises Exception('No account found for this login'); our override
        # turns that into a silent no-op so the controller cannot leak existence.
        result = (
            self.env["res.users"]
            .sudo()
            .reset_password("definitely-not-a-user@example.invalid")
        )
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestResetPasswordEnumeration(HttpCase):
    def _reset_url(self, email):
        return f"/web/reset_password?signup_email={email}"

    def test_signup_email_probe_redirects_uniformly(self):
        # A bare signup_email (no token) is only ever an enumeration probe.
        # Both an existing and a non-existing address must produce the same
        # uniform redirect to /web/login, with no existence-dependent branch.
        existing = self.env["res.users"].search([], limit=1)
        self.assertTrue(existing, "need at least one user")

        resp_known = self.url_open(
            self._reset_url(existing.email or existing.login),
            allow_redirects=False,
        )
        resp_unknown = self.url_open(
            self._reset_url("definitely-not-a-user@example.invalid"),
            allow_redirects=False,
        )

        for resp in (resp_known, resp_unknown):
            self.assertIn(resp.status_code, (302, 303))
            self.assertIn("/web/login", resp.headers.get("Location", ""))

        # The known address must NOT leak the user's real login in the redirect.
        if existing.login and existing.login != (existing.email or existing.login):
            self.assertNotIn(existing.login, resp_known.headers.get("Location", ""))
