# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from werkzeug.exceptions import NotFound

from odoo.http import request, route
from odoo.tools import str2bool

from odoo.addons.rpc.controllers import RPC

# When this config parameter is not truthy, the JSON-RPC endpoint is disabled
# (returns 404). It defaults to disabled because we have no JSON-RPC consumers;
# set it to "1"/"True" to re-enable should an integration ever need it.
JSONRPC_ENABLED_PARAM = "odoo_webclient_hardening.jsonrpc_enabled"


class RpcHardening(RPC):
    """Disable deprecated/unused external RPC endpoints.

    XML-RPC (``/xmlrpc`` and ``/xmlrpc/2``) is always disabled. JSON-RPC
    (``/jsonrpc``) is disabled unless explicitly enabled via the
    ``odoo_webclient_hardening.jsonrpc_enabled`` config parameter. Disabled
    routes respond with 404 so they appear absent rather than merely
    forbidden. None of these endpoints are used by the web client, which calls
    ``/web/dataset/call_kw`` instead.
    """

    @route()
    def xmlrpc_1(self, service):
        raise NotFound()

    @route()
    def xmlrpc_2(self, service):
        raise NotFound()

    @route()
    def jsonrpc(self, service, method, args):
        if not self._jsonrpc_enabled():
            raise NotFound()
        return super().jsonrpc(service, method, args)

    @staticmethod
    def _jsonrpc_enabled():
        if not request.db:
            return False
        value = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(JSONRPC_ENABLED_PARAM, "False")
        )
        return str2bool(value, False)
