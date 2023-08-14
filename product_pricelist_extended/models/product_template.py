# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv import expression


class ProductTemplate(models.Model):

    _inherit = "product.template"

    assortment_id = fields.Many2one(comodel_name="ir.filters", domain=[('is_assortment', '=', True), ('show_in_filters', '=', True)], store=False, search="_search_assortment_filter", help='Technical field to filter by assortment membership')

    def _search_assortment_filter(self, operator, value):
        # TODO: Roadmap - support direct id searches in a dropdown search and set, not set
        value = self.env['ir.filters'].search([('name', operator, value), ('is_assortment', '=', True), ('show_in_filters', '=', True)]).ids
        model = "template" if self._name == 'product.template' else "product"
        domain = []
        for ir_filter in self.env['ir.filters'].browse(value):
            if not domain:
                domain.extend(getattr(ir_filter, f"_get_eval_domain_{model}")())
            else:
                domain = expression.OR([domain, getattr(ir_filter, f"_get_eval_domain_{model}")()])
        return domain
