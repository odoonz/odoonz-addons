# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    item_assortment_ids = fields.One2many(
        comodel_name="product.pricelist.assortment.item",
        inverse_name="pricelist_id",
        string="Assortment items",
    )

    def action_launch_assortment_update(self):
        """
        Action to execute update of assortment items
        :return: dict
        """
        for item_assortment in self.mapped("item_assortment_ids"):
            item_assortment._update_assortment_items()
        return True

    @api.model
    def _get_pricelist_assortment_to_update(self):
        """
        Get every pricelists related to an assortment (and active)!
        :return: self recordset
        """
        return self.env["product.pricelist"].search(
            [("item_assortment_ids", "!=", False)]
        )

    @api.model
    def cron_assortment_update(self):
        pricelists = self._get_pricelist_assortment_to_update()
        pricelists.action_launch_assortment_update()
        return True

    @api.constrains('item_assortment_ids')
    def _check_assortment_items(self):
        if self.env.context.get('migration_mode'):
            return
        for record in self:
            for model, applied_on in [('product.product', '0_product_variant'), ('product.template', '1_product'), ('product.category', '2_product_category')]:
                records = record.item_assortment_ids.filtered(lambda x: x.applied_on == applied_on)
                seen = set()
                for rec in records:
                    current_len = len(seen)
                    items = self.env[model].search(rec.get_eval_domain()).ids
                    seen.update(items)
                    if len(items) != len(seen) - current_len:
                        raise ValidationError(f'Records should not overlap. Overlap found in {rec.name}')
