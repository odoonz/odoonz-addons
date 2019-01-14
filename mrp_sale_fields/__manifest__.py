# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Sale Fields',
    'summary': "Adds fields from sale order when linked",
    'version': '12.0.1.2.0',
    'license': 'AGPL-3',
    'author': 'Open For Small Business Ltd',
    'website': 'https://o4sb.com',
    'depends': ['mrp', 'sale_stock', 'sale'],
    'data': [
        'views/mrp_production.xml',
        'views/sale_order.xml',
    ],
}
