# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests

from odoo import models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_rpc(self, endpoint, access_token):
        if "graph.microsoft.com" in endpoint:
            return requests.get(
                endpoint,
                headers={"Authorization": "Bearer {}".format(access_token)},
            ).json()
        return super()._auth_oauth_rpc(endpoint, access_token)
