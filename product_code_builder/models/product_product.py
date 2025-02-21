# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from collections import defaultdict
from string import Template

from odoo import _, api, fields, models
from odoo.exceptions import MissingError

DEFAULT_REFERENCE_SEPARATOR = ""
PLACE_HOLDER_4_MISSING_VALUE = "/"


class ReferenceMask(Template):
    pattern = r"""\[(?:
                    (?P<escaped>\[) |
                    (?P<named>[^\]]+?)\] |
                    (?P<braced>[^\]]+?)\] |
                    (?P<invalid>)
                    )"""


class ProductProduct(models.Model):
    _inherit = "product.product"

    manual_code = fields.Boolean(
        string="Manual code", compute="_compute_manual_code", readonly=False, store=True
    )
    default_code = fields.Char(
        compute="_compute_default_code", store=True, index="trigram", readonly=False
    )

    @api.model_create_multi
    def create(self, values):
        products = super().create(values)
        products._render_default_code()
        return products

    @api.depends("default_code")
    def _compute_manual_code(self):
        for product in self:
            product.manual_code = bool(
                product.default_code != product._get_rendered_default_code()
            )

    @staticmethod
    def _extract_token(s):
        if not s:
            return set()
        pattern = re.compile(r"\[([^\]]+?)\]")
        return set(pattern.findall(s))

    @api.constrains(
        "reference_mask",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id",
        "attribute_line_ids.attribute_id.name",
    )
    def _check_reference_mask(self, mask):
        tokens = self._extract_token(mask)
        attribute_names = set()
        for line in self.attribute_line_ids:
            attribute_names.add(line.attribute_id.name)
        if not tokens.issubset(attribute_names):
            raise MissingError(
                _("Found unrecognized attribute name in Partcode Template")
            )

    def _get_rendered_default_code(self):
        product_attrs = defaultdict(str)
        reference_mask_str = self.reference_mask or ""
        reference_mask = ReferenceMask(reference_mask_str)
        for value in self.product_template_attribute_value_ids:
            if value.attribute_id.code:
                product_attrs[value.attribute_id.name] += value.attribute_id.code
            if value.product_attribute_value_id.code:
                product_attrs[value.attribute_id.name] += (
                    value.product_attribute_value_id.code
                )
        all_attrs = self._extract_token(self.reference_mask)
        missing_attrs = all_attrs - set(product_attrs.keys())
        missing = dict.fromkeys(missing_attrs, PLACE_HOLDER_4_MISSING_VALUE)
        product_attrs.update(missing)
        default_code = reference_mask.safe_substitute(product_attrs)
        return default_code

    def _compute_default_code(self):
        for product in self:
            if not product.reference_mask or product.manual_code:
                continue
            # product._sanitize_reference_mask(product)
            product.default_code = product._get_rendered_default_code()
