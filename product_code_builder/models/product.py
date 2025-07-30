# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from collections import defaultdict
from string import Template

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, ValidationError

DEFAULT_REFERENCE_SEPARATOR = ""
PLACE_HOLDER_4_MISSING_VALUE = "/"


class ReferenceMask(Template):
    pattern = r"""\[(?:
                    (?P<escaped>\[) |
                    (?P<named>[^\]]+?)\] |
                    (?P<braced>[^\]]+?)\] |
                    (?P<invalid>)
                    )"""  # type: ignore


def extract_token(s):
    if not s:
        return set()
    pattern = re.compile(r"\[([^\]]+?)\]")
    return set(pattern.findall(s))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    reference_mask = fields.Char(
        string="Partcode Template",
        copy=False,
        help="A template for building internal references of a "
        "variant generated from this template.\n"
        "Example:\n"
        "A product named ABC with 2 attributes: Size and Color:\n"
        "Product: ABC\n"
        "Color: Red(r), Yellow(y), Black(b)  #Red, Yellow, Black are "
        "the attribute value, `r`, `y`, `b` are the corresponding code\n"
        "Size: L (l), XL(x)\n"
        "When setting the partcode template to `[Color]-[Size]`, the "
        "default code on the variants will be something like `r-l` "
        "`b-l` `r-x` ...\n"
        "If you like, You can even have the attribute name appear more"
        " than once in the template e.g. `fancyA/[Size]~[Color]~[Size]`"
        " When saved, the default code on variants will be something like"
        ' `fancyA/l~r~l` (for variant with Color "Red" and Size "L") '
        '`fancyA/x~y~x` (for variant with Color "Yellow" and Size "XL")\n'
        'Note: make sure characters "[,]" do not appear in your '
        "attribute name",
    )

    @api.constrains(
        "reference_mask",
        "attribute_line_ids",
    )
    def _check_reference_mask(self):
        if not self.reference_mask:
            return
        tokens = extract_token(self.reference_mask)
        attribute_names = {line.attribute_id.name for line in self.attribute_line_ids}
        if not tokens.issubset(attribute_names):
            raise MissingError(
                _("Found unrecognized attribute name in Partcode Template")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.new(vals)
            if not vals.get("reference_mask") and product.attribute_line_ids:
                attribute_names = [
                    f"[{line.attribute_id.name}]" for line in product.attribute_line_ids
                ]
                default_mask = DEFAULT_REFERENCE_SEPARATOR.join(attribute_names)
                vals["reference_mask"] = default_mask
        products = super().create(vals_list)
        return products

    def write(self, vals):
        if "reference_mask" in vals and not vals["reference_mask"]:
            if len(self) > 1 and any([(t.attribute_line_ids for t in self)]):
                raise ValidationError(
                    _(
                        "Cannot write default reference mask to multiple "
                        "variant templates at once."
                    )
                )
            elif self.attribute_line_ids:
                attribute_names = []
                for line in self.attribute_line_ids:
                    attribute_names.append(f"[{line.attribute_id.name}]")
                default_mask = DEFAULT_REFERENCE_SEPARATOR.join(attribute_names)
                vals["reference_mask"] = default_mask
        result = super().write(vals)
        if "attribute_line_ids" in vals and "reference_mask" not in vals:
            # To trigger default code creation
            for tmpl in self:
                tmpl.write({"reference_mask": tmpl.reference_mask})
        if vals.get("reference_mask"):
            for tmpl in self:
                product_obj = self.env["product.product"]
                cond = [("product_tmpl_id", "=", tmpl.id), ("manual_code", "=", False)]
                products = product_obj.with_context(active_test=False).search(cond)
                for product in products:
                    product._compute_default_code()
        return result


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
        products._compute_default_code()
        return products

    @api.depends("default_code")
    def _compute_manual_code(self):
        for product in self:
            product.manual_code = bool(
                product.default_code != product._get_rendered_default_code()
            )

    def _get_rendered_default_code(self):
        product_attrs = defaultdict(str)
        reference_mask_str = self.product_tmpl_id.reference_mask or ""
        reference_mask = ReferenceMask(reference_mask_str)
        for value in self.product_template_attribute_value_ids:
            if value.attribute_id.code:
                product_attrs[value.attribute_id.name] += value.attribute_id.code
            if value.product_attribute_value_id.code:
                product_attrs[value.attribute_id.name] += (
                    value.product_attribute_value_id.code
                )
        all_attrs = extract_token(self.reference_mask)
        missing_attrs = all_attrs - set(product_attrs.keys())
        missing = dict.fromkeys(missing_attrs, PLACE_HOLDER_4_MISSING_VALUE)
        product_attrs.update(missing)
        default_code = reference_mask.safe_substitute(product_attrs)
        return default_code

    @api.depends(
        "product_tmpl_id.reference_mask",
        "manual_code",
        "product_template_attribute_value_ids.product_attribute_value_id.code",
    )
    def _compute_default_code(self):
        for product in self:
            template = product.product_tmpl_id
            if not template.reference_mask or product.manual_code:
                continue
            product.default_code = product._get_rendered_default_code()
