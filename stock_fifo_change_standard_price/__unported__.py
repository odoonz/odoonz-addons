# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Fifo Change Standard Price",
    "summary": """
        Allows to Update Product Fifo Costs""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["stock_account", "stock"],
    "data": [
        "wizards/stock_fifo_change_standard_price.xml",
        "views/product_template.xml",
        "wizards/stock_change_standard_price.xml",
    ],
}
