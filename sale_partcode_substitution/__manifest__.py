# Copyright 2014 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Partcode Replacement",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales & Purchases",
    "summary": "Allows all products of a sale order to be updated by "
    "substituting part of their partcode",
    "author": "MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["sale"],
    "data": [
        "wizard/sale_partcode_replacement.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product_product.xml"],
    "installable": False,
}
