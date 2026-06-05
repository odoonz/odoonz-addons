# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from werkzeug.urls import url_encode

from odoo.http import request, route

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class AuthSignupHardening(AuthSignupHome):
    """Remove the account-enumeration oracle from ``/web/reset_password``.

    On a GET, the core controller looks the address up and 302-redirects to
    ``/web/login?login=<actual login>`` when a user with that email already
    exists (so someone re-clicking an activated signup link lands on login),
    but renders the reset form (200) otherwise. That existence-dependent
    response, plus the leak of the real ``login``, lets an attacker probe
    ``?signup_email=<addr>`` to enumerate accounts.

    Every Odoo-generated activation/reset link carries a ``token`` alongside
    ``signup_email`` (see ``res.partner._get_signup_url_for_action``), so a bare
    ``signup_email`` with no token is only ever an enumeration probe. We
    therefore short-circuit that case to a uniform redirect to ``/web/login``
    echoing the value supplied, identical whether or not the account exists.
    Token-bearing links (genuine activation, stale-link bounce) and POST
    submissions fall through to the original behaviour untouched.
    """

    @route()
    def web_auth_reset_password(self, *args, **kw):
        if self._owh_is_signup_email_probe(kw):
            query = url_encode({"login": kw["signup_email"], "redirect": "/web"})
            return request.redirect(f"/web/login?{query}")
        return super().web_auth_reset_password(*args, **kw)

    @staticmethod
    def _owh_is_signup_email_probe(kw):
        if request.httprequest.method == "POST":
            return False
        if not kw.get("signup_email"):
            return False
        return not (kw.get("token") or request.session.get("auth_signup_token"))
