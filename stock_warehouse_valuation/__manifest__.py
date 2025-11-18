{
    "name": "Stock Warehouse Temporal Valuation",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Warehouse",
    "summary": "Provides temporal stock valuation by location and warehouse",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": [
        "stock_account",
    ],
    "data": [
        "security/stock_valuation_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/stock_valuation_history_views.xml",
    ],
    "installable": True,
}
