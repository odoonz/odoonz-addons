# © 2015 Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char()

    def write(self, vals):
        result = super().write(vals)
        if "code" in vals:
            self._render_default_code()
        return result

    def _render_default_code(self):
        attribute_line_obj = self.env["product.template.attribute.line"]
        product_obj = self.env["product.product"]
        for attribute in self:
            attribute_lines = attribute_line_obj.search(
                [("attribute_id", "=", attribute.id)]
            )
            for line in attribute_lines:
                prod_cond = [
                    ("product_tmpl_id", "=", line.product_tmpl_id.id),
                    ("manual_code", "=", False),
                    ("reference_mask", "!=", False),
                ]
                products = product_obj.with_context(active_test=False).search(prod_cond)
                for product in products:
                    product._compute_default_code()
