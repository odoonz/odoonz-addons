# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Reordering Rule Quantity Multiple",
    "summary": "Round reordering-rule quantities to an integer multiple, "
    "optionally without exceeding the maximum quantity",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["stock", "purchase_stock", "mrp"],
    "data": ["views/stock_orderpoint_views.xml"],
    "installable": True,
}
