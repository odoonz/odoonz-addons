# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, models
from odoo.tools import OrderedSet


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """If 'run' is called on a kit, this override is made in order to call
        the original 'run' method with the values of the components of that kit.

        Note: This is an override of the original method in mrp. The only change is
        to use the product from the bom line data, rather than the bom line.
        As commented.
        """
        procurements_without_kit = []
        product_by_company = defaultdict(OrderedSet)
        for procurement in procurements:
            product_by_company[procurement.company_id].add(procurement.product_id.id)
        kits_by_company = {
            company: self.env["mrp.bom"]._bom_find(
                self.env["product.product"].browse(product_ids),
                company_id=company.id,
                bom_type="phantom",
            )
            for company, product_ids in product_by_company.items()
        }
        for procurement in procurements:
            bom_kit = kits_by_company[procurement.company_id].get(
                procurement.product_id
            )
            if bom_kit:
                order_qty = procurement.product_uom._compute_quantity(
                    procurement.product_qty, bom_kit.product_uom_id, round=False
                )
                qty_to_produce = order_qty / bom_kit.product_qty
                boms, bom_sub_lines = bom_kit.explode(
                    procurement.product_id, qty_to_produce
                )
                for bom_line, bom_line_data in bom_sub_lines:
                    bom_line_uom = bom_line.product_uom_id
                    quant_uom = bom_line.product_id.uom_id
                    # Here we change to use the bom_line_data product,
                    # rather than the bom_line.product_id
                    product = bom_line_data.get("product", bom_line.product_id)
                    # recreate dict of values since each child has its own bom_line_id
                    values = dict(procurement.values, bom_line_id=bom_line.id)
                    (
                        component_qty,
                        procurement_uom,
                    ) = bom_line_uom._adjust_uom_quantities(
                        bom_line_data["qty"], quant_uom
                    )
                    procurements_without_kit.append(
                        self.env["procurement.group"].Procurement(
                            product,
                            component_qty,
                            procurement_uom,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            values,
                        )
                    )
            else:
                procurements_without_kit.append(procurement)
        return super().run(procurements_without_kit, raise_user_error=raise_user_error)
