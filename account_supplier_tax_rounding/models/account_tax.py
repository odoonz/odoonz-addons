# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def compute_all(
        self,
        price_unit,
        currency=None,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
        handle_price_include=True,
        include_caba_tags=False,
        rounding_method=None,
    ):
        """Intercept call to compute all, to set context key to rounding
        method set on supplier then call super
        """
        if partner and self._is_purchase_tax():
            rounding_method = partner.tax_calc_method
        return super().compute_all(
            price_unit,
            currency=currency,
            quantity=quantity,
            product=product,
            partner=partner,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=include_caba_tags,
            rounding_method=rounding_method,
        )

    def _is_purchase_tax(self):
        return self.filtered(lambda t: t.type_tax_use == "purchase")
