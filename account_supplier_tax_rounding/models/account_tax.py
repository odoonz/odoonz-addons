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
    ):
        if (
            partner
            and partner.tax_calc_method == "round_per_line"
            and self.filtered(lambda t: t.type_tax_use == "purchase")
        ):
            return super(AccountTax, self.with_context(round=True)).compute_all(
                price_unit,
                currency=currency,
                quantity=quantity,
                product=product,
                partner=partner,
                is_refund=False,
                handle_price_include=True,
            )
        else:
            return super().compute_all(
                price_unit,
                currency=currency,
                quantity=quantity,
                product=product,
                partner=partner,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )
