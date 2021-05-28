# Copyright 2020 RIL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentsFolder(models.Model):

    _inherit = "documents.folder"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit", string="Operating Unit"
    )
