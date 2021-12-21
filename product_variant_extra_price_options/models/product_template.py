# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        """Overrides method to provide combination ids (ptavs) in context so we
        can reuse in price extra calculation
        """
        quantity = self.env.context.get("quantity", add_qty)
        context = dict(
            self.env.context,
            quantity=quantity,
            pricelist=pricelist.id if pricelist else False,
        )
        product_template = self.with_context(context)
        combination = (
            combination or product_template.env["product.template.attribute.value"]
        )
        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(
                parent_combination
            )
        self = self.with_context(combination=combination.ids)
        return super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        """Overides method to set current_attributes_price_extra
        based on the price_extra methods
        """
        if price_type == "list_price" and self._context.get("combination"):
            ptavs = self.env["product.template.attribute.value"].browse(
                self._context.get("combination")
            )
            price_extra = self.env["product.product"]._compute_price_extra_from_ptavs(
                ptavs
            )
            self = self.with_context(current_attributes_price_extra=price_extra)
        return super().price_compute(
            price_type, uom=uom, currency=currency, company=company
        )
