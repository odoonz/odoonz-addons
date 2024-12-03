# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, api, fields, models


class SalePriceRecalculation(models.TransientModel):
    _inherit = ["price.recalculation"]
    _name = "sale.price.recalculation"
    _description = "Sale Price Recalculation"

    pricelist_id = fields.Many2one("product.pricelist", "Pricelist")
    copy_quote_id = fields.Many2one("sale.order", "Copy Quote")
    line_ids = fields.One2many(
        "sale.price.recalculation.line",
        "price_recalculation_id",
        "Lines",
    )

    @api.onchange("as_at_date")
    def _onchange_as_at_date(self):
        if self.pricelist_id:
            self.onchange_pricelist_id()
        elif self.copy_quote_id:
            self.onchange_quote_id()

    @api.onchange("pricelist_id")
    def _onchange_pricelist_id(self):
        """Clear discounts and re-determine unit prices from selected pricelist"""
        if not self.pricelist_id:
            return
        pricelist = self.pricelist_id.with_context(**self._set_context())
        for line in self.line_ids.with_context(**self._set_context()):
            line.discount = 0.0
            line._update_pricing(self.as_at_date, pricelist)

    @api.onchange("copy_quote_id")
    def _onchange_copy_quote_id(self):
        """Re-determine prices when quote or date changes"""
        pricelist = self.copy_quote_id.pricelist_id
        if pricelist:
            for line in self.line_ids.with_context(**self._set_context()):
                line.update_pricelist_lines(self.as_at_date, pricelist)
        quoted_prices = self._get_quoted_prices(self.copy_quote_id)
        for line in self.line_ids:
            orig_price = line.price_unit
            line.price_unit = self._get_line_quoted_price(
                line.product_id, quoted_prices, orig_price
            )
            if line.price_unit != orig_price:
                line.discount = 0.0
                line.price_subtotal = line.price_unit * line.qty
                line.price_total = line.price_subtotal * (1 + line.effective_tax_rate)

    def _set_context(self):
        ctx = super()._set_context()
        ctx.update(
            {
                "warehouse_id": self.name.warehouse_id.id,
                "partner_id": self.name.partner_id.commercial_partner_id.id,
                "date": self.as_at_date,
            }
        )
        return ctx

    def _get_quoted_prices(self, quote):
        """
        Refactored method out of onchange_quote_id as useful
        elsewhere
        :param quote:
        :return: dictionary of template prices on  quote
        """
        return {
            ql.product_id.product_tmpl_id.id: (
                ql.price_unit * (1.0 - (ql.discount / 100.0)),
                ql.product_id.list_price,
            )
            for ql in quote.order_line
        }

    @staticmethod
    def _get_line_quoted_price(product, quoted_prices, orig_price):
        """
        Refactored method out of onchange_quote_id as useful
        elsewhere
        :return: price (float)
        """
        tmpl_id = product.product_tmpl_id.id
        if tmpl_id not in quoted_prices:
            return orig_price
        if quoted_prices[tmpl_id][1]:
            ratio = product.list_price / quoted_prices[tmpl_id][1]
        else:
            ratio = 0.0
        return quoted_prices[tmpl_id][0] * ratio

    @staticmethod
    def _get_lines(order):
        def get_effective_tax_rate(line):
            if line.price_subtotal:
                return (line.price_total - line.price_subtotal) / line.price_subtotal
            else:
                taxes = line.tax_id.compute_all(
                    1,
                    line.order_id.currency_id,
                    1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
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
                    "qty": ol.product_uom_qty,
                    "discount": ol.discount,
                    "price_unit": ol.price_unit,
                    "price_subtotal": ol.price_subtotal,
                    "price_total": ol.price_total,
                    "effective_tax_rate": get_effective_tax_rate(ol),
                },
            )
            for ol in order.order_line
            if not ol.display_type
        ]

    def _prepare_quote_related_vals(self):
        return {}

    def _reprice_lines(self, lines):
        msgs = []
        for line in lines:
            order_line = line.name.with_context(
                ignore_protected_fields=["price_unit", "discount", "price_subtotal"]
            )
            if (order_line.price_unit != line.price_unit) or (
                line.name.discount != line.discount
            ):
                if line.qty == 0:
                    msgs.append(
                        _(
                            "<li>{name}: was ${old_value:.2f} ea - "
                            "now ${new_value:.2f} ea</li>"
                        ).format(
                            name=order_line.name,
                            old_value=order_line.price_unit,
                            new_value=line.price_unit,
                        )
                    )
                else:
                    msgs.append(
                        _(
                            "<li>{name}: was ${old_value:.2f} ea - "
                            "now ${new_value:.2f} ea</li>"
                        ).format(
                            name=order_line.name,
                            old_value=order_line.price_subtotal / line.qty,
                            new_value=line.price_subtotal / line.qty,
                        )
                    )
                order_line.write(
                    {"discount": line.discount, "price_unit": line.price_unit}
                )

                order_line.invoice_lines.with_context(check_move_validity=False).write(
                    {
                        "discount": line.discount,
                        "price_subtotal": line.price_subtotal,
                        "price_unit": line.price_unit,
                    }
                )
        return msgs

    def action_write(self):
        self.ensure_one()
        self._check_write_constraints()
        order = self.name
        header_msgs = [_("<p><b>Pricing Updated</b></p>")]
        msgs = ["<ul>"]
        vals = {}
        pricelist_id = order.pricelist_id.id
        if self.pricelist_id:
            pricelist_id = self.pricelist_id.id
        elif self.copy_quote_id:
            pricelist_id = self.copy_quote_id.pricelist_id.id
            vals.update(self._prepare_quote_related_vals())
            header_msgs.append(
                _("<p>Price updated from <b>{quote}</b></p>").format(
                    quote=self.copy_quote_id.name,
                )
            )
        if pricelist_id != order.pricelist_id.id:
            header_msgs.append(
                _(
                    "<p>Pricelist changed from <b>{old_name}</b> to "
                    "<b>{new_name}</b></p>"
                ).format(
                    old_name=order.pricelist_id.name,
                    new_name=self.pricelist_id.name,
                )
            )
            vals["pricelist_id"] = pricelist_id
        if order.invoice_ids:
            msgs.append(_("<p><em>The draft invoice has also been updated.</em></p>"))
        vals.update(self._prepare_other_vals())
        order.write(vals)
        msgs.extend(self._reprice_lines(self.line_ids))
        if len(msgs) > 1:
            msgs.append("</ul><br/>")
        else:
            msgs = []
        order.invoice_ids._compute_amount()
        msgs = header_msgs + msgs
        if msgs:
            body = "".join(msgs)
            order.message_post(body=Markup(body))
        return {}
