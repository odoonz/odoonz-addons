# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def _check_lock_date(self):
        res = super()._check_lock_date()
        for move in self:
            lock_date = move.journal_id._check_lock_date(move)
            if lock_date:
                raise UserError(
                    _(
                        "The transaction date is too old for the "
                        "%s lock policy."
                    )
                    % move.journal_id.name
                )
        return res
