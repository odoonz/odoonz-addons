# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    import_reference = fields.Char(
        help="Import File Reference for the primary supplier of this product.",
    )
    external_reference = fields.Char(
        string="Supplier Reference",
        compute="_compute_external_reference",
        inverse="_inverse_external_reference",
        store=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.external_reference")
    def _compute_external_reference(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.external_reference = (
                template.product_variant_ids.external_reference
            )
        for template in self - unique_variants:
            template.external_reference = False

    def _inverse_external_reference(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.external_reference = (
                    template.external_reference
                )
