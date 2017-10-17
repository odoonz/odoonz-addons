# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Dynamic Lines',
    'description': """
        Allows to dynamically switch a bom's products based on the product selected""",
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly',
    'website': 'https://o4sb.com',
    'depends': ['mrp'
    ],
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_bom_line.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    # 'demo': [
    #     'demo/mrp_bom_line.xml',
    # ],
}
