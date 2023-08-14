# Copyright 2022 O4SB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Intracompany User",
    "summary": """
        New "Intracompany User" for executing actions restricted to a single company""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "O4SB",
    "website": "https://github.com/OCA/project",
    "depends": ["base"],
    "data": [
        "views/company_view.xml",
    ],
}
