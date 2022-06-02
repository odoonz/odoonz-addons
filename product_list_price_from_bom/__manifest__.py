# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product List Price From Bom",
    "summary": """
        Calculates List Price from component retail prices - very much WIP""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["product", "mrp_account", "product_configurator"],
    "data": [
        "views/product_product.xml",
        "views/product_template.xml",
    ],
}
