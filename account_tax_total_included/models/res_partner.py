# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extends res.partner to add tax total included functionality"""

    _inherit = "res.partner"

    force_tax_total_included = fields.Boolean(
        string="GST Inclusive",
        default=False,
        help="When enabled, forces all taxes to be computed as price included for this partner",
    )

    def _commercial_fields(self):
        return super()._commercial_fields() + ["force_tax_total_included"]
