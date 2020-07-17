# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Filter Prodlot Qty",
    "summary": """
        Filters production lots by availability in location""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["mrp", "base_view_inheritance_extension"],
    "data": ["views/mrp_product_produce.xml"],
}
