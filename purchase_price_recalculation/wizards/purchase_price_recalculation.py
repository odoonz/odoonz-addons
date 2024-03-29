# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PurchasePriceRecalculation(models.TransientModel):
    """Purchase Price Recalculation"""

    _inherit = ["price.recalculation"]
    _name = "purchase.price.recalculation"
    _description = __doc__

    name = fields.Many2one("purchase.order", "Purchase Order")
    line_ids = fields.One2many(
        "purchase.price.recalculation.line", "price_recalculation_id", "Lines"
    )

    @staticmethod
    def _get_lines(purchase):
        def get_effective_tax_rate(line):
            if line.price_subtotal:
                return (line.price_total - line.price_subtotal) / line.price_subtotal
            else:
                taxes = line.taxes_id.compute_all(
                    1,
                    line.order_id.currency_id,
                    1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                return (taxes["total_included"] - taxes["total_excluded"]) / taxes[
                    "total_excluded"
                ]

        return [
            (
                0,
                0,
                {
                    "name": ol.id,
                    "product_id": ol.product_id.id,
                    "qty": ol.product_qty,
                    "price_unit": ol.price_unit,
                    "price_subtotal": ol.price_subtotal,
                    "price_total": ol.price_total,
                    "effective_tax_rate": get_effective_tax_rate(ol),
                },
            )
            for ol in purchase.order_line
        ]

    def _set_context(self):
        ctx = super()._set_context()
        ctx.update({"warehouse_id": self.name.warehouse_id.id})
        return ctx

    def _check_write_constraints(self):
        """
        Check write constraints for orders that can't be updated
        Note: Caller ensures one record
        """
        super()._check_write_constraints()
        if self.name.picking_ids.filtered(lambda p: p.state == "done"):
            raise ValidationError(
                _(
                    "You cannot change pricing on an order that has "
                    "already been received."
                )
            )

    def action_write(self):
        self.ensure_one()
        self._check_write_constraints()
        order = self.name
        header_msgs = [_("<p><b>Pricing Updated</b></p>")]
        msgs = ["<ul>"]
        vals = {}
        if order.invoice_ids:
            msgs.append(
                _("<p><emph>The draft invoice has also " "been updated.</emph></p>")
            )
        vals.update(self._prepare_other_vals())
        order.write(vals)
        for line in self.line_ids:
            order_line = line.name
            if order_line.price_unit != line.price_unit:
                msgs.append(
                    _("<li>{0}: was ${1:.2f} ea - " "now ${2:.2f} ea</li>").format(
                        order_line.name,
                        order_line.price_subtotal / line.qty,
                        line.price_subtotal / line.qty,
                    )
                )
                order_line.write({"price_unit": line.price_unit})
                order_line.invoice_lines.with_context(check_move_validity=False).write(
                    {
                        "price_subtotal": line.price_subtotal,
                        "price_unit": line.price_unit,
                    }
                )
                order_line.move_ids.write(
                    {"price_unit": order_line._get_stock_move_price_unit()}
                )
        if len(msgs) > 1:
            msgs.append("</ul><br/>")
        else:
            msgs = []
        order.invoice_ids._compute_amount()
        msgs = header_msgs + msgs
        if msgs:
            body = "".join(msgs)
            order.message_post(body=body)
        return {}
