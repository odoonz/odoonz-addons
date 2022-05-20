# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Financial Risk Manager",
    "summary": """
        Adds a seperate security group for managing credit releases""",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["account_financial_risk", "account"],
    "data": [
        "security/financial_risk_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "wizards/partner_set_risk_wizard.xml",
    ],
    "installable": False,
}
