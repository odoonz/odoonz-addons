# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Customer Activity Statement Aged Monthly',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': ' This module enhances customer_activity_statement with option to age monthly',
    "author": "Open For Small Business Ltd",
    'website': 'https://o4sb.com',
    'depends': ["customer_activity_statement"],
    "data": [
        'wizard/customer_activity_statement_wizard.xml',
        'views/statement.xml',
        ],
}
