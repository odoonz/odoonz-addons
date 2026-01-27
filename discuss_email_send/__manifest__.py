# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Discuss Email Send",
    "summary": """
        Send Emails from Discuss""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": [
        "mail",
        "mail_group",
    ],
    "data": [
        "views/mail_channel.xml",
        "views/mail_group.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "discuss_email_send/static/src/xml/*.xml",
        ],
        "mail.assets_discuss_public": [
            "discuss_email_send/static/src/xml/*.xml",
        ],
    },
    "installable": False,
}
