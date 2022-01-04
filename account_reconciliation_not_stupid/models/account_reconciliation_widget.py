# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import AccessError


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _get_statement_line(self, st_line):
        """
        Returns the data required by the bank statement reconciliation
        widget to display a statement line
        """
        data = super()._get_statement_line(st_line)
        data["name"] = " ".join([st_line.payment_ref or "", st_line.ref or ""])
        return data

    @api.model
    def _get_bank_statement_line_partners(self, st_lines):
        """
        This is another bug fix for another dumb error. It could be done
        better, but lets hope its temporary
        :param st_lines:
        :return:
        """
        res = super()._get_bank_statement_line_partners(st_lines)
        new_res = {}
        Partner = self.env["res.partner"]
        company = st_lines[-1:].company_id
        for k, v in res.items():
            try:
                partner = Partner.browse(v)
                # Statement triggers access check
                # pylint: disable=W0104
                partner.name
            except AccessError:
                continue
            else:
                if not partner.company_id or partner.company_id == company:
                    new_res[k] = v
        return new_res

    @api.model
    def _prepare_reconciliation_widget_query(self, statement_line, domain=None):
        if domain is None:
            domain = []
        domain = domain + [("account_id.name", "not ilike", "inventory")]
        return super()._prepare_reconciliation_widget_query(statement_line, domain)

    @api.model
    def get_move_lines_for_bank_statement_line(
        self,
        st_line_id,
        partner_id=None,
        excluded_ids=None,
        search_str=False,
        offset=0,
        limit=None,
        mode=None,
    ):
        return super().get_move_lines_for_bank_statement_line(
            st_line_id,
            partner_id=partner_id,
            excluded_ids=excluded_ids,
            search_str=search_str,
            offset=offset,
            limit=None if partner_id else limit,
            mode=mode,
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
