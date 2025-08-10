# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Tax Total Included",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["account"],
    "summary": "Automatically apply tax total included mode based on partner settings",
    "data": [
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": False,  # Maybe an idea for future, needs a bit more thought and testing
    "auto_install": False,
}
