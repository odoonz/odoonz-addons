# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.depends("name")
    def _compute_code(self):
        for value in self:
            if value.name and not value.code:
                value.code = value.name[0:2].upper()

    code = fields.Char(compute="_compute_code", readonly=False, store=True)
    comment = fields.Text()

    def write(self, vals):
        result = super().write(vals)
        if "code" in vals:
            self.attribute_id._render_default_code()
        return result
