# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Odoo Webclient Hardening",
    "summary": """
        Reduce information disclosure from public web client endpoints""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["web", "rpc", "auth_signup"],
    "data": [],
    "post_load": "post_load",
    "installable": True,
}
