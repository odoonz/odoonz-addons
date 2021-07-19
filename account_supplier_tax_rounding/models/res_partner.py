# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tax_calc_method = fields.Selection(
        [("round_per_line", "Round per Line"), ("round_globally", "Round Globally")],
        "Purchase Tax Rounding",
        default="round_globally",
        help="If you select 'Round per Line' : for each tax, the tax "
        "amount will first be computed and rounded for each "
        "PO or invoice line and then these rounded amounts will be "
        "summed, leading to the total amount for that tax. If you "
        "select 'Round Globally': for each tax, the tax amount will "
        "be computed for each PO/SO/invoice line, then these amounts "
        "will be summed and eventually this total tax amount will be "
        "rounded. If you sell with tax included, you should choose "
        "'Round per line' because you certainly want the sum of your "
        "tax-included line subtotals to be equal to the total amount "
        "with taxes.",
    )
