# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Dynamic Lines',
    'summary': 'Dynamic BoM Transformations - ALPHA',
    'description': """
        NOTE: This module is very Alpha right now after total refactor

        Provides a base to perform dynamic transformations to an exploded
        Bill of Materials, either during explode or raw move generation.

        2 Sample transformations are included:
        - Match Attributes - which seeks to match the bom line with the
          attributes of the parent BoM
        - Scale Weight - scales a bom line measured in kg to the quantity
          being produced""",
    'version': '11.0.2.0.1',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly',
    'website': 'https://o4sb.com',
    'depends': ['mrp'],
    'data': [
        'data/bom_line_xform.xml',
        'security/ir.model.access.csv',
        'views/mrp_bom.xml',
        'views/mrp_bom_line.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'uninstall_hook': 'uninstall_hook',
    # 'demo': [
    #     'demo/mrp_bom_line.xml',
    # ],
}
