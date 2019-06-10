# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _compute_used_in_bom_count(self):
        for template in self:
            template.used_in_bom_count = self.env["mrp.bom"].search_count(
                [("bom_line_ids.product_tmpl_id", "=", template.id)]
            )

    @api.multi
    def action_used_in_bom(self):
        self.ensure_one()
        action = self.env.ref("mrp.mrp_bom_form_action").read()[0]
        action["domain"] = [("bom_line_ids.product_tmpl_id", "=", self.id)]
        return action
