# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from werkzeug.exceptions import HTTPException

from odoo import http
from odoo.exceptions import AccessDenied, UserError

_logger = logging.getLogger(__name__)

# Exceptions whose message is meant for the end user and is therefore safe to
# echo back to anonymous callers. Anything else is treated as an internal
# error and reported generically.
_PUBLIC_SAFE_EXCEPTIONS = (
    UserError,
    AccessDenied,
    HTTPException,
    http.SessionExpiredException,
)

_GENERIC_NAME = "odoo.exceptions.UserError"
_GENERIC_MESSAGE = "Internal Server Error"


def _is_authenticated():
    """Return ``True`` for requests made by a logged-in session.

    ``session.uid`` is populated only once a login is finalized; anonymous
    and ``auth="public"`` requests leave it ``None`` (the public user lives in
    ``env.uid``, not the session), so it is the right signal here.
    """
    try:
        request = http.request
        return bool(request and request.session and request.session.uid)
    except Exception:  # noqa: BLE001 - raised when there is no bound request
        return False


def redact_anonymous_payload(data, exception):
    """Strip internals from a serialized-exception ``dict`` in place.

    Always removes the traceback and context. For exceptions that are not
    user-facing it also genericises the name, message and arguments so that
    nothing about the server internals (paths, SQL, PostgreSQL connection
    details) leaks to anonymous callers.
    """
    data["debug"] = ""
    data["context"] = {}
    if not isinstance(exception, _PUBLIC_SAFE_EXCEPTIONS):
        data["name"] = _GENERIC_NAME
        data["message"] = _GENERIC_MESSAGE
        data["arguments"] = (_GENERIC_MESSAGE,)
    return data


def post_load():
    """Withhold exception internals from unauthenticated callers.

    Odoo serialises every exception raised inside a JSON (``jsonrpc`` /
    ``json2``) request into the response body, including the full traceback.
    That traceback can disclose file paths, SQL and PostgreSQL connection
    details to anyone able to reach a public endpoint. We keep the rich
    payload for logged-in sessions (the web client relies on it) but reduce it
    to a generic error for anonymous callers, while still surfacing genuine
    user-facing messages (``UserError``, HTTP 4xx, ...).
    """
    if getattr(http.serialize_exception, "_owh_patched", False):
        return
    _logger.info("Restricting exception serialization detail to authenticated sessions")
    _serialize_exception_orig = http.serialize_exception

    def serialize_exception(exception, *, message=None, arguments=None):
        data = _serialize_exception_orig(
            exception, message=message, arguments=arguments
        )
        if _is_authenticated():
            return data
        return redact_anonymous_payload(data, exception)

    serialize_exception._owh_patched = True
    http.serialize_exception = serialize_exception
