# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Pricelist Filter",
    "summary": """
        Allows to use filters on pricelists""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/OCA/project",
    "depends": ["product", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/product_pricelist_assortment_item.xml",
        "views/ir_filters.xml",
        "views/product_pricelist_item.xml",
        "views/product_pricelist.xml",
        "views/product_pricelist_assortment_item.xml",
        "data/ir_cron.xml",
    ],
}
