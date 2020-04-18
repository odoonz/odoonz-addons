# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockChangeStandardPrice(models.TransientModel):
    _inherit = "stock.change.standard.price"
    _description = "Change Standard Price"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        product_or_template = self.env[self._context["active_model"]].browse(
            self._context["active_id"]
        )
        if (
            "new_price" in fields_list
            and res.get("new_price", 1.0) == 0.0
            and self._context["active_model"] == "product.template"
        ):
            backstop = product_or_template.product_variant_ids[0].standard_price
            res["new_price"] = (
                product_or_template.product_variant_ids.filtered(
                    lambda s: s.qty_available > 0
                )[-1:].standard_price
                or backstop
            )
        if (
            "counterpart_account_id" in fields_list
            and self.env.user.company_id.anglo_saxon_accounting
        ):
            p = product_or_template
            res["counterpart_account_id"] = (
                p.property_account_creditor_price_difference.id
                or p.categ_id.property_account_creditor_price_difference_categ.id
            )
        return res

    all_variants = fields.Boolean("Update all Variants", default=False)
    show_all_variants = fields.Boolean(
        default=lambda s: s._context.get("active_model", "") == "product.product"
    )
    accounting_date = fields.Date(required=True)

    @api.multi
    def change_price(self):
        """ Overrides change price to update context to enable updating all variants
        and set an as at date"""
        self.ensure_one()
        context = dict(self._context)
        if self.all_variants and self._context["active_model"] == "product.product":
            product = self.env["product.product"].browse(self._context["active_id"])
            context["active_id"] = product.product_tmpl_id.id
            context["active_ids"] = [context["active_id"]]
            context["active_model"] = "product.template"
        if self.accounting_date:
            context["force_period_date"] = self.accounting_date
        super(StockChangeStandardPrice, self.with_context(**context)).change_price()
        return {"type": "ir.actions.act_window_close"}
