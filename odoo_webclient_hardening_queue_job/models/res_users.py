# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def reset_password(self, login):
        """Defer the public password-reset so its timing is constant.

        ``odoo_webclient_hardening`` already makes an unknown login a silent
        no-op so both outcomes render the same message. A *known* login still
        runs synchronous token generation plus an SMTP send
        (``force_send=True`` in ``_action_reset_password``), making the
        response measurably slower than the no-op — a timing oracle that
        re-enables enumeration despite the uniform message.

        When the call originates from an anonymous web request (the public
        ``/web/reset_password`` flow) we hand the real work to a queue job and
        return immediately, so the synchronous response time no longer depends
        on whether the account exists. Authenticated callers (admin-triggered
        resets, scripts, crons) keep the synchronous path so they still see
        mail-server errors directly.
        """
        if self._owh_defer_reset_password():
            self.with_delay(
                description="Password reset (anti-enumeration)"
            )._owh_reset_password_async(login)
            return None
        return super().reset_password(login)

    def _owh_reset_password_async(self, login):
        """Run the actual reset in the background (called by queue_job).

        Delegates to ``super().reset_password`` (the base hardening override)
        which performs the lookup, swallows the unknown-login case and sends
        the mail for a real account. Defined under a distinct name so the job
        does not re-enter :meth:`reset_password` and re-enqueue itself.
        """
        return super().reset_password(login)

    def _owh_defer_reset_password(self):
        """True only for anonymous web requests (the public reset flow)."""
        try:
            return bool(request) and not request.session.uid
        except Exception:  # noqa: BLE001 - no bound request (cron/shell/tests)
            return False
