# Copyright 2024 Moahub Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "SMS ClickSend",
    "summary": """
        Use ClickSend to send SMS""",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "author": "MoaHub Limited",
    "website": "https://github.com/odoonz/odoonz-addons",
    "external_dependencies": {"python": ["clicksend_client"]},
    "depends": ["sms", "iap_alternative_provider"],
    "data": ["views/iap_account_view.xml", "views/sms_sms_view.xml"],
    "installable": True,
}
