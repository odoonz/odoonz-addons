# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_change_line_ids = fields.One2many(
        string="Price Changes",
        comodel_name="product.price.change.line",
        readonly=True,
        inverse_name="product_tmpl_id",
        domain=[("state", "in", ("live", "future"))],
    )


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    price_change_line_ids = fields.One2many(
        string="Price Changes",
        comodel_name="product.variant.price.change.line",
        readonly=True,
        inverse_name="product_tmpl_attribute_value_id",
        domain=[("state", "in", ("live", "future"))],
    )


class ProductProduct(models.Model):

    _inherit = "product.product"

    @staticmethod
    def _get_price_changes_ordered(change_lines, fld):
        return change_lines.filtered(lambda s: s.state in ("live", "future")).sorted(
            key=lambda r: r.price_change_id[fld], reverse=True
        )

    @api.depends("product_template_attribute_value_ids.price_extra")
    def _compute_product_price_extra(self):
        to_uom = None
        if "uom" in self._context:
            to_uom = self.env["uom.uom"].browse([self._context["uom"]])
        effective_date = self._context.get("date")
        if not effective_date:
            effective_date = fields.Date.context_today(self)
        if isinstance(effective_date, datetime):
            effective_date = fields.Date.context_today(self, effective_date)
        if self._context.get("partner_id"):
            commercial_partner_id = (
                self.env["res.partner"]
                .browse(self._context.get("partner_id"))
                .commercial_partner_id.id
            )
            fld = "partner_effective_date"
        else:
            fld = "effective_date"
            commercial_partner_id = False

        for product in self:
            price_extra = 0.0
            for value in product.product_template_attribute_value_ids:
                found = False
                for change in self._get_price_changes_ordered(
                    value.with_context(
                        partner_id=commercial_partner_id
                    ).price_change_line_ids,
                    fld,
                ):
                    if change.price_change_id[fld] <= effective_date:
                        price_extra += change.price_extra
                        found = True
                        break
                if not found:
                    price_extra += value.price_extra
            if to_uom:
                price_extra = product.uom_id._compute_price(price_extra, to_uom)
            product.price_extra = price_extra

    @api.depends("list_price", "price_extra")
    def _compute_product_lst_price(self):
        to_uom = None
        if (
            not self._context.get("uom_already_computed", False)
            and "uom" in self._context
        ):
            to_uom = self.env["uom.uom"].browse([self._context["uom"]])
        effective_date = self._context.get("date")
        if not effective_date:
            effective_date = fields.Date.context_today(self)
        if isinstance(effective_date, datetime):
            effective_date = fields.Date.context_today(self, effective_date)
        partner_id = self._context.get("partner_id", self._context.get("partner", False))
        if partner_id and isinstance(partner_id, models.BaseModel):
            partner_id = partner_id.id
        if partner_id:
            commercial_partner_id = (
                self.env["res.partner"]
                .browse(partner_id)
                .commercial_partner_id.id
            )
            fld = "partner_effective_date"
        else:
            fld = "effective_date"
            commercial_partner_id = False

        # only price changes before effective date, after today
        # first any customer specifc requirements
        for product in self:
            list_price = product.list_price
            for change in self._get_price_changes_ordered(
                product.with_context(
                    partner_id=commercial_partner_id
                ).price_change_line_ids,
                fld,
            ):
                if change.price_change_id[fld] <= effective_date:
                    list_price = change.list_price
                    break
            if to_uom:
                list_price = product.uom_id._compute_price(list_price, to_uom)
            product.lst_price = list_price + product.price_extra

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        if price_type == "list_price":
            price_type = "lst_price"
        return super(
            ProductProduct,
            self.with_context(uom_already_computed=price_type == "lst_price"),
        ).price_compute(price_type, uom=uom, currency=currency, company=company)
