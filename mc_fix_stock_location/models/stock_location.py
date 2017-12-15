# -*- coding: utf-8 -*-
# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    valuation_in_account_id = fields.Many2one(
        domain="[('internal_type', '=', 'other'),"
               "('deprecated', '=', False),"
               "('company_id', '=', company_id)]"
    )
    valuation_out_account_id = fields.Many2one(
        domain="[('internal_type', '=', 'other'),"
               "('deprecated', '=', False),"
               "('company_id', '=', company_id)]"
    )
