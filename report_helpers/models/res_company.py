# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    def _compute_company_address(self):
        for record in self:
            addresses = record.partner_id.address_get(["delivery", "invoice"])
            record.physical_address_id = addresses["delivery"]
            record.postal_address_id = addresses["invoice"]

    physical_address_id = fields.Many2one(
        comodel_name="res.partner", compute="_compute_company_address"
    )

    postal_address_id = fields.Many2one(
        comodel_name="res.partner", compute="_compute_company_address"
    )
