# Copyright 2021 O4SB Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def _default_operating_unit_id(self):
        if (
            self._context.get("default_move_type", False)
            and self._context.get("default_move_type") != "entry"
        ):
            if self.env.context.get("default_journal_id"):
                journal = self.env["account.journal"].browse(
                    self.env.context["default_journal_id"]
                )
                return (
                    journal.operating_unit_id
                    or self.env["res.users"]
                    .with_context(force_ou_company=journal.company_id.id)
                    .operating_unit_default_get()
                )
            return self.env["res.users"].operating_unit_default_get()
        return False

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit", default=_default_operating_unit_id
    )
