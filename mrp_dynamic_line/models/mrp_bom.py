# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round

_logger = logging.Logger(__name__)


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    def explode(self, product, quantity, picking_type=False):
        boms_done, orig_lines_done = super().explode(
            product, quantity, picking_type=picking_type
        )
        lines_done = []
        for bom_line, line_fields in orig_lines_done:
            for xform in bom_line.xform_ids.filtered(
                lambda bl: bl.application_point == "explode"
            ).sorted("sequence"):
                try:
                    func = getattr(self, "_explode_%s" % xform.technical_name)
                    bom_line, line_fields = func(product, bom_line, line_fields)
                except AttributeError:
                    _logger.error(
                        _("No function found with name _explode_%s")
                        % xform.technical_name
                    )
                if not bom_line:
                    # Its deleted so nothing to xform
                    break
            bom_line and lines_done.append((bom_line, line_fields))
        return boms_done, lines_done

    def _compute_matched_product(self, orig_product, bom_line):
        Product = self.env["product.product"]
        bom_tmpl = bom_line.product_tmpl_id
        search_domain = [("product_tmpl_id", "=", bom_tmpl.id)]
        for value in bom_line.required_value_ids:
            search_domain.append(
                ("product_template_attribute_value_ids", "in", [value.id])
            )
        common_attrs = self.env["product.attribute"]
        op_ptav = orig_product.product_template_attribute_value_ids
        parent_attrs = op_ptav.product_attribute_value_id.attribute_id
        bom_attrs = bom_tmpl.attribute_line_ids.mapped("attribute_id")
        common_attrs = parent_attrs & bom_attrs
        if common_attrs:
            value_ids = [
                v.id
                for v in op_ptav.product_attribute_value_id
                if v.attribute_id.id in set(common_attrs.ids)
            ]
            for value_id in value_ids:
                search_domain.append(
                    (
                        "product_template_attribute_value_ids."
                        "product_attribute_value_id",
                        "in",
                        [value_id],
                    )
                )
        product = Product.search(search_domain)
        if len(product) > 1:
            names = ["  - %s" % p[1] for p in product.name_get()]
            raise ValidationError(
                _(
                    "The BoM Line %s in BoM %s is matching too many "
                    "products.  Expected < 1 and received:\n%s"
                )
                % (
                    bom_line.product_tmpl_id.name,
                    bom_line.bom_id.name,
                    "\n".join(names),
                )
            )
        elif not product:
            product = bom_line.product_id
        return self.env["xform.substitution.map"]._get_substitute(product)

    def _explode_match_attributes(self, orig_product, bom_line, line_fields):
        product = self._compute_matched_product(orig_product, bom_line)
        line_fields.update({"product": product})
        return bom_line.with_context(product=product), line_fields

    def _explode_scale_weight_kg(self, orig_product, bom_line, line_fields):
        bom = bom_line.bom_id
        product = bom_line._context.get("product", orig_product)
        parent_weight = (
            bom.product_uom_id._compute_quantity(bom.product_qty, orig_product.uom_id)
            * orig_product.weight
            or 1.0
        )
        weight_factor = 1 / (product.weight or 1.0)
        qty = (
            parent_weight
            * line_fields["original_qty"]
            * bom_line.product_qty
            * weight_factor
        )
        rounding = bom_line.product_uom_id.rounding
        line_fields.update(
            qty=float_round(qty, precision_rounding=rounding, rounding_method="UP")
        )
        return bom_line, line_fields
