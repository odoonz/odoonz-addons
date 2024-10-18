# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Accounting Entry Lock Policy",
    "summary": "Specify a policy to automatically set lock dates",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["account"],
    "data": [
        "views/account_lock_policy.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
    ],
    "installable": False,
}
