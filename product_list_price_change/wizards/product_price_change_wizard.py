# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPriceChangeWizard(models.TransientModel):

    _name = "product.price.change.wizard"
    _rec_name = "price_change_id"
    _description = "Add Price Changes in Bulk"

    price_change_id = fields.Many2one(
        comodel_name="product.price.change", default=lambda s: s._context.get("active_id")
    )
    product_tmpl_ids = fields.Many2many(comodel_name="product.template")
    percent_change = fields.Float()
    overwrite_existing = fields.Boolean(default=True)

    @api.multi
    def update_price_change_record(self):
        for wizard in self:
            records_to_remove = wizard.price_change_id.product_line_ids.filtered(
                lambda s: s.product_tmpl_id.id in wizard.product_tmpl_ids.ids
            )
            if records_to_remove:
                if wizard.overwrite_existing:
                    records_to_remove.unlink()
                else:
                    raise ValidationError(
                        "The selected products already exist in the price change list:\n -"
                        + "\n - ".join(records_to_remove.mapped("name"))
                    )
            lines_to_create = []
            for product in self.product_tmpl_ids:
                lines_to_create.append(
                    {
                        "price_change_id": wizard.price_change_id.id,
                        "product_tmpl_id": product.id,
                        "percent_change": wizard.percent_change,
                        "list_price": 0.0,
                    }
                )
            new_lines = self.env["product.price.change.line"].create(lines_to_create)
            new_lines._change_percent()
        return {"type": "ir.actions.act_window_close"}
