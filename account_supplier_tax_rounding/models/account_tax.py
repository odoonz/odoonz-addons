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
        fixed_multiplicator=1,
    ):
        """Intercept call to compute all, to set context key to rounding
        method set on supplier then call super
        """
        if (
            partner
            and partner.tax_calc_method == "round_per_line"
            and self.filtered(lambda t: t.type_tax_use == "purchase")
        ):
            self = self.with_context(round=True)
        return super().compute_all(
            price_unit,
            currency=currency,
            quantity=quantity,
            product=product,
            partner=partner,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=include_caba_tags,
            fixed_multiplicator=fixed_multiplicator,
        )
