# Copyright 2022 Graeme Gellatly, MoaHub Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def evaluate_risk_message(self, partner):
        self.ensure_one()
        if (
            not partner.credit_limit
            and self.company_id.enforce_limit_sale
            and (partner.risk_total + self.amount_total)
            > self.company_id.allowed_min_sale
        ):
            return _("No credit limit set yet for this customer.\n")
        return super().evaluate_risk_message(partner)
