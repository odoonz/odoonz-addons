# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Supplier Tax Rounding",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": " Open for Small Business Ltd",
    "website": "https://github.com/OCA/project",
    "depends": ["account", "base"],
    "summary": "This module allows for the tax setting to be be set per "
    "supplier.  It assumes global rounding set on the company.",
    "data": ["views/res_partner.xml"],
    "installable": False,
}
