# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Accounting Journal Lock Policy',
    'summary': "Specify journal specific lock policies",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly',
    'website': 'https://o4sb.com',
    'depends': [
        'account'
    ],
    'data': [
        'views/account_journal.xml',
    ],
}
