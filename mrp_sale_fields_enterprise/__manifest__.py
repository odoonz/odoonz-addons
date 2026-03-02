# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mrp Sale Fields Enterprise",
    "summary": """
        Adds Sales Fields to workorder views""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["mrp_workorder", "mrp_sale_fields"],
    "data": ["views/mrp_workorder.xml"],
    "installable": True,
}
