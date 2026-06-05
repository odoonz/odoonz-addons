# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Odoo Webclient Hardening - Queue Job",
    "summary": """
        Defer public password-reset work to a background job to remove the
        reset/signup timing oracle""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["odoo_webclient_hardening", "queue_job"],
    "data": [],
    "installable": True,
    "auto_install": True,
}
