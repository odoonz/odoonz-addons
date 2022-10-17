# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Variant Extra Price Options",
    "summary": """
        Allows to specify more advanced variant pricing rules""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly, O4SB Ltd",
    "website": "https://o4sb.com",
    "depends": ["product", "sale"],
    "data": [
        "views/product_attribute.xml",
        "views/product_template_attribute_value.xml",
        "views/variant_templates.xml",
        "security/ir.model.access.csv",
    ],
}
