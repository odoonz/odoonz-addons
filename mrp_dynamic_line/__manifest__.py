# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mrp Dynamic Lines",
    "summary": "Dynamic BoM Transformations",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": " MoaHub Ltd",
    "website": "https://github.com/odoonz/odoonz-addons",
    "depends": ["mrp", "product", "sale"],
    "data": [
        "data/bom_line_xform.xml",
        "security/ir.model.access.csv",
        "views/mrp_bom.xml",
        "views/mrp_bom_line.xml",
        "views/xform_substitution_map.xml",
    ],
    "installable": False,
}
