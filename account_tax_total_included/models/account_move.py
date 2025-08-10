# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    """Extends account.move to add tax total included functionality"""

    _inherit = "account.move"

    force_tax_total_included = fields.Boolean(
        string="GST Inclusive",
        compute="_compute_force_tax_total_included",
        readonly=False,
        store=True,
        help="When enabled, forces all taxes to be computed as price included",
    )

    @api.depends("partner_id.force_tax_total_included", "move_type", "partner_id")
    def _compute_force_tax_total_included(self):
        """Compute the tax total included flag from the partner"""
        for move in self:
            if (
                move.move_type
                in ("out_invoice", "out_refund", "in_invoice", "in_refund")
                and move.partner_id
            ):
                move.force_tax_total_included = move.partner_id.force_tax_total_included
            else:
                move.force_tax_total_included = False

    def _prepare_product_base_line_for_taxes_computation(self, line):
        """Override to force special_mode to total_included when requested"""
        base_line = super()._prepare_product_base_line_for_taxes_computation(line)

        if self.force_tax_total_included:
            base_line["special_mode"] = "total_included"

        return base_line

    @api.onchange("force_tax_total_included")
    def _onchange_force_tax_total_included(self):
        """Onchange to force tax total included"""
        self.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )._compute_totals()
        # No I don't know why this is needed, but it is
        self.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )._compute_totals()
