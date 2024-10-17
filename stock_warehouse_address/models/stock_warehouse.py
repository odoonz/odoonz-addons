# Copyright 2017 MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    postal_address_id = fields.Many2one(
        comodel_name="res.partner", string="Postal Address"
    )
    partner_id = fields.Many2one(string="Physical Address")
