# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.http import route

from odoo.addons.web.controllers.webclient import WebClient


class WebClientHardening(WebClient):
    @route()
    def version_info(self):
        """Stop the anonymous endpoint from fingerprinting the server.

        ``/web/webclient/version_info`` is ``auth="none"`` and otherwise
        returns the exact Odoo version, version tuple and serie (including the
        ``e`` edition marker), letting anyone identify the release to target
        known CVEs. The web client only uses this route as a connectivity ping
        (the lost-connection handler and the ``home`` / ``reload`` client
        actions ignore the payload), and the version it actually consumes
        comes from ``session_info``. So we drop the version fields and keep
        only ``protocol_version`` for any RPC client that expects a dict.
        """
        return {"protocol_version": 1}
