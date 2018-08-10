# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestTxtReport(common.TransactionCase):

    def test_report(self):
        report_object = self.env["ir.actions.report"]
        report_name = "qweb_txt_report.report_res_users_csv"
        report = report_object._get_report_from_name(report_name)
        docs = self.env["res.users"].search([("id", "=", 1)])
        self.assertEqual(report.report_type, "qweb-text")
        rep = report.render(docs.ids, {})
        self.assertIn(b"admin", rep[0])
