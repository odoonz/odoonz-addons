# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SalePriceRecalculation(models.TransientModel):
    """Sale Price Recalculation"""

    _inherit = ["price.recalculation"]
    _name = "sale.price.recalculation"
    _description = __doc__

    copy_quote_id = fields.Many2one("sale.order", "Copy Quote")
    line_ids = fields.One2many(
        "sale.price.recalculation.line", "price_recalculation_id", "Lines"
    )

    @api.multi
    def _prepare_quote_related_vals(self):
        return {}

    @api.onchange("total", "tax_incl")
    def _onchange_balance_to_total(self):
        if not self.total:
            return
        for line in self.line_ids:
            line.discount = 0.0
        return super()._onchange_balance_to_total()

    @api.onchange("pricelist_id")
    def onchange_pricelist_id(self):
        for line in self.line_ids:
            line.discount = 0.0
        return self.update_pricelist_lines(self.pricelist_id)

    @api.multi
    def _set_context(self):
        ctx = super()._set_context()
        ctx.update({"warehouse_id": self.name.warehouse_id.id})
        return ctx

    def _get_quoted_prices(self, quote):
        """
        Refactored method out of onchange_quote_id as useful
        elsewhere
        :param quote:
        :return: dictionary of template prices on  quote
        """
        return {
            ql.product_id.product_tmpl_id.id: (ql.price_unit, ql.product_id.list_price)
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

    @api.onchange("copy_quote_id")
    def onchange_quote_id(self):
        self.update_pricelist_lines(self.copy_quote_id.pricelist_id)
        quoted_prices = self._get_quoted_prices(self.copy_quote_id)
        for line in self.line_ids:
            orig_price = line.price_unit
            line.price_unit = self._get_line_quoted_price(
                line.product_id, quoted_prices, orig_price
            )
            if line.price_unit != orig_price:
                line.price_subtotal = line.price_unit * line.qty
                line.price_total = line.price_subtotal * (1 + line.effective_tax_rate)

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

    @api.multi
    def action_write(self):
        self.ensure_one()
        self._check_write_constraints()
        order = self.name
        header_msgs = [_(u"<p><b>Pricing Updated</b></p>")]
        msgs = [u"<ul>"]
        vals = {}
        pricelist_id = order.pricelist_id.id
        if self.pricelist_id:
            pricelist_id = self.pricelist_id.id
        elif self.copy_quote_id:
            pricelist_id = self.copy_quote_id.pricelist_id.id
            vals.update(self._prepare_quote_related_vals())
            header_msgs.append(
                _(u"<p>Price updated from <b>{0}</b></p>").format(
                    self.copy_quote_id.name
                )
            )
        if pricelist_id != order.pricelist_id.id:
            header_msgs.append(
                _(u"<p>Pricelist changed from <b>{0}</b> to " u"<b>{1}</b></p>").format(
                    order.pricelist_id.name, self.pricelist_id.name
                )
            )
            vals["pricelist_id"] = pricelist_id
        if order.invoice_ids:
            msgs.append(
                _(u"<p><emph>The draft invoice has also " u"been updated.</emph></p>")
            )
        vals.update(self._prepare_other_vals())
        order.write(vals)
        msgs.extend(self._reprice_lines(self.line_ids))
        if len(msgs) > 1:
            msgs.append(u"</ul><br/>")
        else:
            msgs = []
        order.invoice_ids.compute_taxes()
        msgs = header_msgs + msgs
        if msgs:
            body = "".join(msgs)
            order.message_post(body=body)
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
                try:
                    msgs.append(
                        _(
                            u"<li>{0}: was ${1:.2f} ea - " u"now ${2:.2f} ea</li>"
                        ).format(
                            order_line.name,
                            order_line.price_subtotal / line.qty,
                            line.price_subtotal / line.qty,
                        )
                    )
                except ZeroDivisionError:
                    msgs.append(
                        _(
                            u"<li>{0}: was ${1:.2f} ea - " u"now ${2:.2f} ea</li>"
                        ).format(
                            order_line.name, order_line.price_unit, line.price_unit
                        )
                    )
                order_line.write(
                    {"discount": line.discount, "price_unit": line.price_unit}
                )
                order_line.invoice_lines.write(
                    {
                        "discount": line.discount,
                        "price_subtotal": line.price_subtotal,
                        "price_unit": line.price_unit,
                    }
                )
        return msgs
