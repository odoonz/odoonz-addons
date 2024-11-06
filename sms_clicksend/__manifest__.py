# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "SMS ClickSend",
    "summary": """
        Use ClickSend to send SMS""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Moahub Limited",
    "website": "https://github.com/OCA/project",
    "external_dependencies": {"python": ["clicksend_client"]},
    "depends": ["sms", "iap_alternative_provider"],
    "data": ["views/iap_account_view.xml", "views/sms_sms_view.xml"],
}
