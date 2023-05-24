# Copyright 2014 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pricelist Extensions",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales & Purchases",
    "author": "Open For Small Business Ltd",
    "website": "https://o4sb.com",
    "depends": ["product", "sale"],
    "summary": "This module implements many2many products in pricelists.",
    "data": [
        "views/product_pricelist_view.xml",
        "views/product_price_category_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product.price.category.csv"],
    "installable": False,
}
