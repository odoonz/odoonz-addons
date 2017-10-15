# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Price Recalculation',
    'description': """
        Allows to update the pricing on confirmed sales orders prior to invoice""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly',
    'website': 'https://o4sb.com',
    'depends': [
        'price_recalculation',
    ],
    'data': [
        'wizards/sale_price_recalculation.xml',
    ],
    'demo': [
    ],
}
