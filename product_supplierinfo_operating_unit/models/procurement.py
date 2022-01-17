# © 2015-17 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015-17 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origin, values):
        res = super()._prepare_purchase_order(company_id, origin, values)
        ou_id = False
        if self.operating_unit_id:
            ou_id = (self.operating_unit_id.id,)
        elif "group_id" in values[0] and values[0].get("group_id"):
            group = values[0].get("group_id")
            sale = group.sale_id
            if sale:
                ou_id = sale.operating_unit_id.id
        res.update({"operating_unit_id": ou_id, "requesting_operating_unit_id": ou_id})
        return res

    def _run_buy(self, procurements):
        ou_id = False
        try:
            proc = procurements[0][0].values
            group = proc.get("group_id")
            ou_base = group.sale_id or proc.get("warehouse_id")
            ou_id = ou_base.operating_unit_id.id
        except Exception:
            pass
        return super(StockRule, self.with_context(operating_unit=ou_id))._run_buy(
            procurements
        )
