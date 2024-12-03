# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class PriceRecalculation(models.AbstractModel):
    _name = "price.recalculation"
    _description = "Recalculate Price"

    partner_id = fields.Many2one("res.partner", "Partner")
    total = fields.Float("Balance To", digits="Account")
    tax_incl = fields.Boolean()
    name = fields.Many2one("sale.order", "Sale Order")
    precision = fields.Integer(
        "Unit Price Precision",
        default=lambda s: s.env["decimal.precision"].precision_get("Account"),
        help="The number of decimal places to use for the unit price",
    )
    as_at_date = fields.Date("Reprice as at", required=True)

    @staticmethod
    def _get_lines(obj):
        raise NotImplementedError

    @api.model
    def default_get(self, flds):
        res = super().default_get(flds)
        if len(self.env.context.get("active_ids", [])) != 1:
            return res
        obj = self.env[self._context["active_model"]].browse(
            self._context["active_ids"][0]
        )
        if "name" in flds:
            res.update(name=obj.id)
        if "partner_id" in flds:
            res.update(partner_id=obj.partner_id.id)
        if "line_ids" in flds:
            res.update(line_ids=self._get_lines(obj))
        if "as_at_date" in flds:
            res.update(as_at_date=obj.date_order)
        return res

    @api.onchange("total", "tax_incl")
    def _onchange_balance_to_total(self):
        if not self.total:
            return
        fld = "price_total" if self.tax_incl else "price_subtotal"
        running_total = self.total
        running_lines_total = sum([x[fld] for x in self.line_ids])
        lowest_qty = (None, float("inf"))
        prec = self.env["decimal.precision"].precision_get("Account")
        for line in self.line_ids.sorted(key=lambda r: r.qty, reverse=True):
            if line.qty < lowest_qty[1]:
                lowest_qty = (line, line.qty)
            weight = running_total / running_lines_total
            try:
                price = line[fld] / line.qty * weight
            except ZeroDivisionError:
                price = line.price_unit
            else:
                running_lines_total -= line[fld]
            if fld == "price_total":
                price /= 1 + line.effective_tax_rate
            price = float_round(price, self.precision)
            line.price_unit = price
            line.price_subtotal = line.price_unit * line.qty
            line.price_total = line.price_subtotal * (1 + line.effective_tax_rate)
            running_total -= line[fld]
            if not running_lines_total:
                break
        if float_round(running_total, prec) and lowest_qty[0]:
            line = lowest_qty[0]
            extra = running_total / line.qty
            if fld == "price_total":
                extra /= 1 + line.effective_tax_rate
            price = float_round(line.price_unit + extra, self.precision)
            if price > 0.0:
                line.price_unit = float_round(price, self.precision)
                line.price_subtotal = line.price_unit * line.qty
                line.price_total = line.price_subtotal * (1 + line.effective_tax_rate)

    def _check_write_constraints(self):
        """
        Check write constraints for orders that can't be updated
        Note: Caller ensures one record
        """
        # Temp until we can figure out how to price draft invoice
        # if self.name.invoice_ids.filtered(lambda i:
        # i.state not in ("draft", "cancel")):
        if self.name.invoice_ids:
            raise ValidationError(
                _(
                    "You cannot change pricing on an order that has "
                    "already been invoiced."
                )
            )
        return True

    def _prepare_other_vals(self):
        """
        Hook method for extension of action_write method
        :return: dict of field_name: value pairings
        """
        return {}

    def _set_context(self):  # pragma: no cover
        """Hook method for setting a custom context by model"""
        return {}
