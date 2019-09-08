# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)


class XformSubstitutionMap(models.Model):
    _name = "xform.substitution.map"
    _description = "BoM Transformation Substitution Map"
    _rec_name = "dest_product_id"

    src_product_ids = fields.Many2many(
        comodel_name="product.product", string="Source Products", required=True
    )
    dest_product_id = fields.Many2one(
        comodel_name="product.product", string="Destination Product", required=True
    )

    @api.model
    def _get_substitute(self, src_product):
        subst_map = self.search([("src_product_ids", "in", src_product.ids)])
        if subst_map:
            return subst_map[0].dest_product_id
        return src_product
