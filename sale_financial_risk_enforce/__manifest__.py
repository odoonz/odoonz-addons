# Copyright 2022 Graeme Gellatly, MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Financial Risk Enforce",
    "summary": """
        Enforces credit limit is set before allowing an order to be confirmed""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly, MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["sale_financial_risk", "account_financial_risk_manager"],
    "data": ["views/res_config_settings.xml"],
    "installable": False,
}
