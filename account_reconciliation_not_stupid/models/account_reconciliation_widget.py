# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _domain_move_lines_for_reconciliation(
        self, st_line, aml_accounts, partner_id, excluded_ids=None, search_str=False
    ):
        domain = expression.AND(
            [
                [
                    (
                        "account_id.internal_type",
                        "in",
                        ("receivable", "payable", "liquidity"),
                    )
                ],
                super()._domain_move_lines_for_reconciliation(
                    st_line,
                    aml_accounts,
                    partner_id,
                    excluded_ids=excluded_ids,
                    search_str=search_str,
                ),
            ]
        )
        return domain

    @api.model
    def get_move_lines_for_bank_statement_line(
        self,
        st_line_id,
        partner_id=None,
        excluded_ids=None,
        search_str=False,
        offset=0,
        limit=None,
    ):
        return super().get_move_lines_for_bank_statement_line(
            st_line_id,
            partner_id=partner_id,
            excluded_ids=excluded_ids,
            search_str=search_str,
            offset=offset,
            limit=None if partner_id else limit,
        )

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
