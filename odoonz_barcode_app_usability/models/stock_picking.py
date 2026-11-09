# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from ast import literal_eval

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _barcode_find_by_prior_transfer(self, barcode, picking_type=None):
        """Open transfers whose previous transfer is named ``barcode``.

        The pick is printed before the pack exists, so the slip can only
        carry the pick number. Scanning that number later has to find the
        transfer that was created from it.

        Name matching is case-insensitive so a Caps Lock keyboard-wedge
        scan still finds the prior transfer.
        """
        if not barcode:
            return self.browse()
        domain = [
            ("move_ids.move_orig_ids.picking_id.name", "=ilike", barcode),
            ("state", "not in", ("cancel", "done", "draft")),
        ]
        if picking_type:
            domain.append(("picking_type_id", "=", picking_type.id))
        return self.search(domain, order="id")

    @api.model
    def _barcode_action_for_pickings(self, pickings):
        """Barcode operations list limited to ``pickings``."""
        picking_types = pickings.picking_type_id
        if len(picking_types) == 1:
            action = picking_types._get_action(
                "stock_barcode.stock_picking_action_kanban"
            )
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcode.stock_picking_action_kanban"
            )
            action["context"] = dict(literal_eval(action["context"]))
        context = dict(action["context"])
        for key in (
            "search_default_available",
            "search_default_to_do_transfers",
            "search_default_name",
        ):
            context.pop(key, None)
        action["context"] = context
        action["domain"] = [("id", "in", pickings.ids)]
        return action

    @api.model
    def _barcode_filter_by_name(self, barcode, picking_type):
        """Filter open transfers of ``picking_type`` whose name matches ``barcode``.

        Uses ``=ilike`` so Caps Lock on a USB scanner does not miss the
        pick document.
        """
        if not barcode or not picking_type:
            return self.browse()
        return self.search(
            [
                ("picking_type_id", "=", picking_type.id),
                ("state", "not in", ("cancel", "done", "draft")),
                ("name", "=ilike", barcode),
            ],
            limit=1,
        )

    @api.model
    def filter_on_barcode(self, barcode):
        result = super().filter_on_barcode(barcode)
        if not result.get("warning"):
            return result
        picking_type = self.env["stock.picking.type"].browse(
            self.env.context.get("active_id")
        )
        named = self._barcode_filter_by_name(
            barcode, picking_type if picking_type else None
        )
        if named:
            action = picking_type._get_action(
                "stock_barcode.stock_picking_action_kanban"
            )
            action["context"] = dict(action["context"])
            action["context"].update(
                {
                    "active_id": picking_type.id,
                    "search_default_name": named.name,
                }
            )
            return {"action": action}
        successors = self._barcode_find_by_prior_transfer(
            barcode, picking_type=picking_type if picking_type else None
        )
        if not successors:
            return result
        if len(successors) == 1:
            return {"action": successors.action_open_picking_client_action()}
        return {"action": self._barcode_action_for_pickings(successors)}
