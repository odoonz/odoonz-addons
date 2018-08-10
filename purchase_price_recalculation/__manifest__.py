# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Price Recalculation',
    'summary': "Allows to update the pricing of confirmed purchase orders "
               "prior to reception",
    'version': '11.0.1.1.0',
    'license': 'AGPL-3',
    'author': ' Open for Small Business Ltd',
    'website': 'https://o4sb.com',
    'depends': [
        'price_recalculation',
        'purchase',
    ],
    'data': [
        'wizards/purchase_price_recalculation.xml',
    ],
    'demo': [
    ],
}
