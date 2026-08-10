# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product List Price Change",
    "summary": """
        Supports temporal list price changes for products""",
    "version": "19.0.1.0.2",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["product", "sale"],
    "data": [
        "wizards/product_price_change_wizard.xml",
        "security/ir.model.access.csv",
        "views/product_price_rise.xml",
        "data/ir_cron_data.xml",
    ],
    "installable": True,
}
