# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrExpenseSheet(models.Model):

    _inherit = "hr.expense.sheet"

    @api.model_create_multi
    def create(self, vals_list):
        """Copies attachments from expense lines to expense sheet at create"""
        sheets = super().create(vals_list)
        for sheet in sheets:
            attachments = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", "hr.expense"),
                    ("res_id", "in", self.expense_line_ids.ids),
                ]
            )
            for attachment in attachments:
                attachment.copy({"res_model": "hr.expense.sheet", "res_id": sheet.id})
        return sheet
