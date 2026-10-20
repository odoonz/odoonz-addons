# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Barcode Lot Prompt",
    "summary": """
        Pick or create a lot on the inventory count screen""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["stock_barcode"],
    "assets": {
        "web.assets_backend": [
            "stock_barcode_lot_prompt/static/src/**/*.js",
            "stock_barcode_lot_prompt/static/src/**/*.xml",
            "stock_barcode_lot_prompt/static/src/**/*.scss",
        ],
    },
    "installable": True,
}
