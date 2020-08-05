# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductPriceChange(models.Model):

    _name = "product.price.change"
    _description = "Product Price Change"
    _order = "effective_date desc, id"

    name = fields.Char(required=True)
    effective_date = fields.Date(
        required=True, readonly=True, states={"draft": [("readonly", False)]}
    )
    partner_effective_date = fields.Date(compute="_compute_partner_effective_date")
    description = fields.Html()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("future", "Future"),
            ("live", "Live"),
            ("cancel", "Cancel"),
        ],
        required=True,
        default="draft",
    )

    product_line_ids = fields.One2many(
        string="Products",
        comodel_name="product.price.change.line",
        inverse_name="price_change_id",
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )
    variant_line_ids = fields.One2many(
        string="Variants",
        comodel_name="product.variant.price.change.line",
        inverse_name="price_change_id",
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )
    impl_delay_ids = fields.One2many(
        string="Implementation Delays",
        comodel_name="product.price.change.implementation_delay",
        inverse_name="price_change_id",
        states={
            "cancel": [("readonly", True)],
            "future": [("readonly", True)],
            "live": [("readonly", True)],
        },
    )

    def action_confirm(self):
        for record in self.filtered(lambda s: s.state == "draft"):
            record.state = "future"

    def action_cancel(self):
        for record in self:
            if record.state == "live":
                raise UserError(
                    _("Cannot cancel a previously implemented pricing change")
                )
            record.state = "cancel"

    def action_draft(self):
        for record in self:
            if record.state == "live":
                raise UserError(
                    _("Cannot cancel a previously implemented pricing change")
                )
            record.state = "draft"

    def _compute_partner_effective_date(self):
        partner_id = self._context.get("partner_id")
        if partner_id:
            tag_ids = (
                self.env["res.partner"]
                .browse(partner_id)
                .commercial_partner_id.category_id.ids
            )
        else:
            tag_ids = False
        for record in self:
            partner_effective_date = record.effective_date
            break_outer = False
            if partner_id and tag_ids and record.impl_delay_ids:
                for delay in record.impl_delay_ids:
                    if break_outer:
                        break
                    for tag_id in delay.included_categories.ids:
                        if tag_id in tag_ids:
                            partner_effective_date = delay.effective_date
                            break_outer = True
                            break
            record.partner_effective_date = partner_effective_date

    def _update_future_pricing(self):
        for line in self.product_line_ids:
            if line.list_price != line.product_tmpl_id.list_price:
                line.product_tmpl_id.list_price = line.list_price
        for line in self.variant_line_ids:
            if line.product_tmpl_attribute_value_id.price_extra != line.price_extra:
                line.product_tmpl_attribute_value_id.price_extra = line.price_extra

    @api.model
    def perform_list_price_update(self):
        today = fields.Date.context_today(self)
        to_upd = self.search([("effective_date", "<=", today)])
        for change in to_upd:
            if change.state == "future" and change.effective_date <= today:
                change._update_future_pricing()
                change.state = "live"
