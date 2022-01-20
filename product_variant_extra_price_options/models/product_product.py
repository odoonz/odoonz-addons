# Copyright 2021 Graeme Gellatly, O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _compute_product_price_extra(self):
        """Replaces method to set current_attributes_price_extra
        based on the price_extra methods
        @note: This makes this currently incompatible with price change module
        """
        for product in self:
            ptavs = product.product_template_attribute_value_ids
            product.price_extra = sum(self._compute_price_extra_from_ptavs(ptavs))

    def _compute_price_extra_from_ptavs(self, ptavs):
        """ Computes Price Extra by dispatching to ptavs price_extra_method
        """
        price_extra_dict = {pev.attribute_id.id: pev.price_extra for pev in ptavs}
        for ptav in ptavs:
            try:
                price_extra_dict = getattr(
                    ptav, "_pre_calc_%s" % ptav.price_extra_method
                )(price_extra_dict, ptavs)
            except AttributeError:
                continue
        for ptav in ptavs:
            try:
                price_extra_dict = getattr(ptav, "_calc_%s" % ptav.price_extra_method)(
                    price_extra_dict
                )
            except AttributeError:
                continue
        return price_extra_dict.values()

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        if self._context.get("no_variant_attributes_price_extra"):
            ptavs = self.env["product.template.attribute.value"].browse(
                self._context.get("combination")
            )
            price_extra = tuple(
                [sum(self._compute_price_extra_from_ptavs(ptavs)) - self.price_extra]
            )
            self = self.with_context(no_variant_attributes_price_extra=price_extra)
        return super().price_compute(
            price_type, uom=uom, currency=currency, company=company
        )
