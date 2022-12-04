# Copyright 2022 Graeme Gellatly, O4SB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Filter Show Qty Mrp Glue Bugfix",
    "summary": """
        Fixes context incompatibility of mrp, stock_filter_qty and stock_show_qty""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly, O4SB",
    "website": "https://o4sb.com",
    "depends": [
        "mrp",
        "stock_prodlot_qty",
    ],
    "auto_install": True,
    "data": [
        "views/stock_move_line_view.xml",
    ],
}
