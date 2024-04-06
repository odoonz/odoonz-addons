# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product List Price From Bom",
    "summary": """
        Calculates List Price from component retail prices - very much WIP""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/OCA/project",
    "depends": ["product", "mrp_account", "product_configurator"],
    "data": [
        "views/mrp_workcenter.xml",
        "views/product_product.xml",
        "views/product_template.xml",
    ],
    "installable": True,
}
