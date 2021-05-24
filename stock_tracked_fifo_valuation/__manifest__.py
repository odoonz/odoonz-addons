# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Tracked Fifo Valuation",
    "summary": """
        Selects in moves of same lot for cost tracking (more like actual cost)""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["stock", "stock_account"],
    "data": ["views/stock_valuation_layer.xml"],
}
