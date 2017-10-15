# -*- coding: utf-8 -*-
# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Variant Default Code",
    "version": "11.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "contributors": [
        "OdooMRP team",
        "Avanzosc",
        "Serv. Tecnol. Avanzados - Pedro M. Baeza",
        "Shine IT(http://www.openerp.cn)",
        "Tony Gu <tony@openerp.cn>",
        "Graeme Gellatly <g@o4sb.com>",
        ],
    "license": "AGPL-3",
    "category": "Product",
    "website": "http://www.odoo-community.org",
    "depends": ['product',
                ],
    "data": ['views/product_attribute_value_view.xml',
             'views/product_view.xml',
             'views/product_attribute_view.xml'
             ],
    "demo": ['demo/product.attribute.csv',
             'demo/product.attribute.value.csv'],
    "installable": True
}
