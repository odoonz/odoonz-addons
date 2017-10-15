# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Dynamic Weight',
    'description': """
        Allows to dynamically scale a bom line's product qty on the product selected""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly',
    'website': 'https://o4sb.com',
    'depends': ['mrp_dynamic_lines'
    ],
    'data': [
        'views/mrp_bom.xml',
    ],
    # 'demo': [
    #     'demo/mrp_bom_line.xml',
    # ],
}
