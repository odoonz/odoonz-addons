# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleCodeReplacement(models.TransientModel):
    _name = "sale.code.replacement"
    _description = "Sale Partcode Substitution"

    from_code = fields.Char("From", default="???", required=True)
    to_code = fields.Char("To", default="???", required=True)

    def change_products_partcode(self):
        self.ensure_one()
        sale = self.env["sale.order"].browse(self._context["active_id"])
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
                        line.product_id = new_part[0]
        return {"type": "ir.actions.act_window_close"}
