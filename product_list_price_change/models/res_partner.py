# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _get_price_change_effective_date(self, price_change):
        self.ensure_one()
        return price_change.with_context(
            partner_id=self.commercial_partner_id.id
        ).partner_effective_date
