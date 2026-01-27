# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleCodeReplacement(models.TransientModel):
    _name = "sale.code.replacement"
    _description = "Sale Partcode Substitution"

    from_code = fields.Char("From", default="???", required=True)
    to_code = fields.Char("To", default="???", required=True)
    keep_manual_pricing = fields.Boolean(default=True)

    def _browse_calling_record(self):
        return self.env[self.env.context["active_model"]].browse(
            self.env.context["active_id"]
        )

    def change_products_partcode(self):
        self.ensure_one()
        sale = self._browse_calling_record()
        self._check_sale_valid_state(sale)
        keep_manual = self.keep_manual_pricing
        for line in sale.order_line:
            replacement_product = self._find_replacement_product(line)
            if replacement_product:
                line.product_id = replacement_product
                if not keep_manual:
                    line._reset_price_unit()
        return {"type": "ir.actions.act_window_close"}

    def _find_replacement_product(self, line):
        if not line.product_id:
            return False
        existing_code = line.product_id.default_code
        if self.from_code in existing_code:
            replacement_code = existing_code.replace(self.from_code, self.to_code)
            replacement_product = self.env["product.product"].search(
                [("default_code", "=", replacement_code)]
            )
            return replacement_product[:1]
        return False

    def _check_sale_valid_state(self, sale):
        if sale.state not in ["draft", "sent"]:
            raise ValidationError(
                _(
                    "Partcodes cannot be changed! Make sure "
                    'the Sales Order is in "Quotation" state!'
                )
            )
