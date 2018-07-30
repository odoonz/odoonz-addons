# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, _
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
                func = getattr(self, "_explode_%s" % xform.technical_name)
                if func:
                    bom_line, line_fields = func(bom_line, line_fields)
                else:
                    _logger.error(
                        _("No function found with name _explode_%s")
                        % xform.technical_name
                    )
                if not bom_line:
                    # Its deleted so nothing to xform
                    break
            bom_line and lines_done.append((bom_line, line_fields))
        return boms_done, lines_done

    @staticmethod
    def _explode_match_attributes(bom_line, line_fields):
        bom_line = bom_line.with_context(product_id=line_fields["product"].id)
        line_fields.update({"product": bom_line.product_id})
        return bom_line, line_fields

    @staticmethod
    def _explode_scale_weight_kg(bom_line, line_fields):
        if bom_line.product_uom_id != bom_line.env.ref(
            "product.product_uom_kgm"
        ):
            _logger.error(
                _(
                    "Scale weight only works for "
                    "raw materials measured in kg."
                )
            )
            return bom_line, line_fields
        bom = bom_line.bom_id
        parent_weight = (
            bom.product_uom_id._compute_quantity(
                bom.product_qty, line_fields["product"].uom_id
            )
            * line_fields["product"].weight
            or 1.0
        )
        qty = parent_weight * line_fields["original_qty"] * bom_line.product_qty
        rounding = bom_line.product_uom_id.rounding
        line_fields.update(
            qty=float_round(
                qty, precision_rounding=rounding, rounding_method="UP"
            )
        )
        return bom_line, line_fields
