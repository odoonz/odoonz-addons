# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _get_statement_line(self, st_line):
        """
        Returns the data required by the bank statement reconciliation
        widget to display a statement line
        """
        data = super()._get_statement_line(st_line)
        data["name"] = " ".join([st_line.name or "", st_line.ref or ""])
        return data

    @api.model
    def _prepare_move_lines(
        self, move_lines, target_currency=False, target_date=False, recs_count=0
    ):
        move_lines = move_lines.sorted(lambda r: (r.date, r.id))
        return super()._prepare_move_lines(
            move_lines,
            target_currency=target_currency,
            target_date=target_date,
            recs_count=recs_count,
        )
