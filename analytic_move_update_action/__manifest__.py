# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Move Update Action",
    "summary": """
        Removes button from account_move_update_analytic and puts in Action menu""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/OCA/project",
    "depends": [
        "account_move_update_analytic",
    ],
    "auto_install": True,
    "data": [
        "views/account_move.xml",
    ],
}
