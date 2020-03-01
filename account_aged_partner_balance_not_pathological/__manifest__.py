# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Aged Partner Balance Not Pathological",
    "summary": """
        The default odoo implementation is optimized for tiny databases, single company,
        without anglosaxon. They refuse to resolve the situation at the expense of
        causing crashes and unacceptable performance on small to midsized databases
        when backdating. This module provides constant performance across all database
        sizes at the cost of 50-100ms performance in the common case of todays date.
        Users won't even notice
        """,
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["account"],
}
