# Copyright 2017 Open For Small Business Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    @api.depends("move_dest_ids")
    def _compute_sale_order(self):
        self._cr.execute(
            """SELECT sm.created_production_id, sol.order_id
        FROM stock_move sm
        LEFT JOIN sale_order_line sol ON sm.sale_line_id = sol.id
        WHERE sm.sale_line_id IS NOT NULL
          AND sm.created_production_id IS NOT NULL
          AND sm.created_production_id IN %s """,
            (tuple(self.ids),),
        )
        production_data = self._cr.fetchall()
        mapped_data = dict(production_data)
        for production in self:
            production.sale_id = mapped_data.get(production.id, False)

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        readonly=True,
        compute="_compute_sale_order",
        store=True,
    )

    partner_id = fields.Many2one(
        related="sale_id.partner_id", string="Customer", store=True
    )
