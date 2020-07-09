# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleCodeReplacement(models.TransientModel):
    _name = "sale.code.replacement"
    _description = "Sale Partcode Substitution"

    from_code = fields.Char("From", default="???", required=True)
    to_code = fields.Char("To", default="???", required=True)

    def _finalize_vals(self, vals, line, product):
        """
        For overriding
        :return: vals dict
        """
        return vals

    def change_products_partcode(self):
        self.ensure_one()
        sale = self.env["sale.order"].browse(self._context["active_id"])
        order_line = self.env["sale.order.line"]
        if sale.state not in ["draft", "sent"]:
            raise ValidationError(
                _(
                    "Partcodes cannot be changed! Make sure "
                    'the Sales Order is in "Quotation" state!'
                )
            )

        prod_pool = self.env["product.product"]

        for line in sale.order_line:
            if line.product_id:
                old_part = line.product_id.default_code
                if old_part.find(self.from_code) != -1:
                    new_partcode = old_part.replace(self.from_code, self.to_code)
                    new_part = prod_pool.search([("default_code", "=", new_partcode)])
                    if new_part:
                        vals = {"product_id": new_part.id}
                        vals.update(
                            order_line._prepare_add_missing_fields(
                                {
                                    "product_uom_qty": line.product_uom_qty,
                                    "order_id": sale.id,
                                    "product_id": new_part.id,
                                }
                            )
                        )
                        vals = self._finalize_vals(vals, line, new_part)
                        line.write(vals)
        # TODO: Why is this needed now:
        #  need to be proven no bug related in production
        sale._amount_all()
        return {}
