# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def reset_password(self, login):
        """Do not reveal whether an account exists for the given login.

        Core ``reset_password`` raises ``Exception('No account found for this
        login')`` when the login/email matches no user, which the
        ``/web/reset_password`` controller surfaces verbatim while a *known*
        login yields "Password reset instructions sent...". That difference is
        a user/email enumeration oracle. We make the unknown-login case a silent
        no-op so both outcomes render the same confirmation message. A genuine
        forgotten-password request for a real account still sends the email.
        """
        users = self.search(self._get_login_domain(login))
        if not users:
            users = self.search(self._get_email_domain(login))
        if not users:
            _logger.info(
                "Password reset requested for unknown login; suppressing disclosure"
            )
            return
        return super().reset_password(login)
