# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    address_id = fields.Many2one(comodel_name="res.partner", string="Address")
