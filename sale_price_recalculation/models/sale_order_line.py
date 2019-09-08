# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_protected_fields(self):
        """
        Override checks for existence of context key 'ignore_protected_fields'
        and removes those fields so they can be written
        :return:
        """
        protected_fields = super()._get_protected_fields()
        if isinstance(self._context.get("ignore_protected_fields"), list):
            protected_fields = list(
                set(protected_fields) - set(self._context["ignore_protected_fields"])
            )
        return protected_fields
