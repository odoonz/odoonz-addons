# Copyright 2014- Odoo Community Association - OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .helper_methods import (
    DEFAULT_REFERENCE_SEPARATOR,
    render_default_code,
    sanitize_reference_mask,
)


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

    @api.model
    def create(self, vals):
        product = self.new(vals)
        if not vals.get("reference_mask") and product.attribute_line_ids:
            attribute_names = []
            for line in product.attribute_line_ids:
                attribute_names.append("[{}]".format(line.attribute_id.name))
            default_mask = DEFAULT_REFERENCE_SEPARATOR.join(attribute_names)
            vals["reference_mask"] = default_mask
        elif vals.get("reference_mask"):
            sanitize_reference_mask(product, vals["reference_mask"])
        return super().create(vals)

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
                    attribute_names.append("[{}]".format(line.attribute_id.name))
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
                    render_default_code(product, vals["reference_mask"])
        return result
