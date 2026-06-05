# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestResetPasswordAsync(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Users = self.env["res.users"].sudo()

    def test_no_request_stays_synchronous(self):
        # Outside a web request (cron/shell/tests) the call must NOT be
        # deferred and must compose with the base override (unknown -> None).
        with patch.object(type(self.Users), "with_delay") as mock_delay:
            result = self.Users.reset_password("nobody@example.invalid")
        mock_delay.assert_not_called()
        self.assertIsNone(result)

    def test_anonymous_request_is_deferred(self):
        # When the request is anonymous, the work is handed to a queue job so
        # the synchronous response time is constant regardless of existence.
        with (
            patch.object(
                type(self.Users), "_owh_defer_reset_password", return_value=True
            ),
            patch.object(type(self.Users), "with_delay") as mock_delay,
        ):
            result = self.Users.reset_password("nobody@example.invalid")
        mock_delay.assert_called_once()
        # The delayed call targets our async wrapper, not reset_password itself.
        mock_delay.return_value._owh_reset_password_async.assert_called_once_with(
            "nobody@example.invalid"
        )
        self.assertIsNone(result)

    def test_async_wrapper_swallows_unknown_login(self):
        # The job body delegates to the base override, which is a silent no-op
        # for an unknown login (no exception, nothing sent).
        result = self.Users._owh_reset_password_async("nobody@example.invalid")
        self.assertIsNone(result)
