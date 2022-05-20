# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product List Price Change",
    "summary": """
        Supports temporal list price changes for products""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["product"],
    "data": [
        "wizards/product_price_change_wizard.xml",
        "security/ir.model.access.csv",
        "views/product_price_rise.xml",
        "data/ir_cron_data.xml",
    ],
    "demo": [
        "demo/product_price_rise.xml",
        "demo/product_price_change_implementation_delay.xml",
        "demo/product_variant_price_change_line.xml",
        "demo/product_price_change_line.xml",
    ],
    "installable": False,
}
