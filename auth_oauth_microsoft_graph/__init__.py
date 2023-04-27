from . import models

from odoo import api, SUPERUSER_ID


def post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # To make Odoo include the Bearer token in the Authorization header, this parameter has to be set
    env["ir.config_parameter"].set_param("auth_oauth.authorization_header", "1")
