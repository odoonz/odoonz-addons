# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Price Recalculation",
    "summary": "Allows to update the pricing of confirmed purchase orders "
    "prior to reception",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["price_recalculation", "purchase"],
    "data": [
        "wizards/purchase_price_recalculation.xml",
        "security/ir.model.access.csv",
    ],
    "installable": False,
}
