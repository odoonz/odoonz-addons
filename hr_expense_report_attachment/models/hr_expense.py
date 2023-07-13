# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HrExpense(models.Model):

    _inherit = "hr.expense"

    def _create_sheet_from_expenses(self):
        """Override to set the attachments on the sheet"""
        sheet = super()._create_sheet_from_expenses()
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "hr.expense"), ("res_id", "in", self.ids)]
        )
        for attachment in attachments:
            attachment.copy({"res_model": "hr.expense.sheet", "res_id": sheet.id})
        return sheet
