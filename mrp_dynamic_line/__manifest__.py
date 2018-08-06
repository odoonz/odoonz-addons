# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mrp Dynamic Lines",
    "summary": "Dynamic BoM Transformations",
    "version": "11.0.3.0.0",
    "license": "AGPL-3",
    "author": " Open for Small Business Ltd",
    "website": "https://o4sb.com",
    "depends": ["mrp", "product"],
    "data": [
        "data/bom_line_xform.xml",
        "security/ir.model.access.csv",
        "views/mrp_bom.xml",
        "views/mrp_bom_line.xml",
        "demo/mrp_dynamic_line.xml"
    ],
    "pre_init_hook": "pre_init_hook",
    "uninstall_hook": "uninstall_hook",
}
