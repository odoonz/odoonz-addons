import odoo.tests

from odoo.addons.account.tests.test_reconciliation import TestReconciliation


@odoo.tests.tagged("post_install", "-at_install")
class TestReconciliationWidget(TestReconciliation):
    def test_get_statement_line(self):
        st_line = self.env["account.bank.statement.line"].search([], limit=1)
        st_line_join = self.env["account.reconciliation.widget"]._get_statement_line(
            st_line
        )
        st_line.name = " ".join([st_line.name or "", st_line.ref or ""])
        self.assertEqual(st_line_join["name"], st_line.name)

    def test_prepare_move_lines(self):
        move_lines = self.env["account.move.line"].search([], limit=3)
        move_lines_sort = move_lines.sorted(lambda r: (r.date, r.id))
        move_lines_prepare = self.env[
            "account.reconciliation.widget"
        ]._prepare_move_lines(move_lines)
        move_lines_sort_prepare = self.env[
            "account.reconciliation.widget"
        ]._prepare_move_lines(move_lines_sort)
        self.assertEqual(move_lines_prepare, move_lines_sort_prepare)
