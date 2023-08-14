# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Anglosaxon Financial",
    "summary": """
        Allows purely financial invoices and credits in anglosaxon environments""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/OCA/project",
    "depends": ["account", "stock_account", "purchase_stock", "sale_stock"],
    "data": ["wizards/account_move_reversal.xml", "views/account_invoice.xml"],
}
