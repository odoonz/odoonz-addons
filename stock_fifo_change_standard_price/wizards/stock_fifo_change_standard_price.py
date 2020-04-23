# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

from odoo.addons import decimal_precision as dp


class StockFifoChangeStandardPrice(models.TransientModel):

    _name = "stock.fifo.change_standard_price"
    _description = "Update FIFO Cost"

    name = fields.Char()
    cost = fields.Float(
        "New Cost for All Lines", digits=dp.get_precision("Product Price")
    )
    accounting_date = fields.Date(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda s: s.env.user.company_id.id
    )
    line_ids = fields.One2many(
        comodel_name="stock.fifo.change_standard_price.line", inverse_name="wizard_id"
    )

    def _get_lines(self, company_id):
        if self._context.get("active_model") == "product.template":
            products = (
                self.env["product.template"]
                .browse(self._context["active_ids"])
                .mapped("product_variant_ids")
                .sorted("default_code")
            )
        elif self._context.get("active_model") == "product.product":
            products = (
                self.env["product.product"]
                .browse(self._context["active_ids"])
                .sorted("default_code")
            )
        else:
            raise ValidationError(
                _("Cannot update FIFO Cost without product or template")
            )
        res = []
        for product in products:
            moves = product._get_fifo_candidates_in_move_with_company(
                move_company_id=company_id
            )
            for move in moves:
                res.append({"move_id": move.id, "new_cost": move.price_unit})
        return res

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "line_ids" in fields_list:
            res["line_ids"] = [
                (0, 0, x) for x in self._get_lines(self.env.user.company_id.id)
            ]
        return res

    @api.onchange("company_id")
    def onchange_company_id(self):
        self.line_ids = self.env["stock.fifo.change_standard_price.line"]
        FifoLine = self.env["stock.fifo.change_standard_price.line"]
        for line in self._get_lines(self.company_id.id):
            self.line_ids += FifoLine.new(line)

    @api.onchange("cost")
    def onchange_cost(self):
        self.ensure_one()
        for line in self.line_ids:
            line.new_cost = self.cost

    def update_costs(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for wizard in self:
            lines_to_update = wizard.line_ids.filtered(
                lambda s: float_compare(
                    s.old_cost, s.new_cost, precision_digits=precision
                )
            )
            if any([line.new_cost == 0.0 for line in lines_to_update]):
                raise ValidationError(_("Can't set a cost to Zero"))
            templates = lines_to_update.mapped("move_id.product_id.product_tmpl_id")
            if wizard.cost:
                templates.mapped("product_variant_ids").write(
                    {"standard_price": wizard.cost}
                )
            accounts = {x.id: x._get_product_accounts() for x in templates}
            for line in lines_to_update:
                move = line.move_id
                original_value = move.remaining_value
                new_value = line.new_cost * move.remaining_qty
                correction_value = original_value - new_value
                move.write(
                    {
                        "price_unit": line.new_cost,
                        "remaining_value": new_value,
                        "value": line.new_cost * move.product_qty,
                    }
                )
                # Has the supplier invoice been done.
                if move.product_id.valuation == "real_time":
                    # If `corrected_value` is 0, absolutely do *not* call `
                    # _account_entry_move`.
                    if move.company_id.currency_id.is_zero(correction_value):
                        continue
                    journal_id, acc_src, acc_dest, acc_valuation = (
                        move._get_accounting_data_for_valuation()
                    )

                    if self.company_id.anglo_saxon_accounting:
                        p = move.product_id
                        account_id = p.property_account_creditor_price_difference.id
                        if not account_id:
                            account_id = (
                                p.categ_id.property_account_creditor_price_difference_categ.id
                            )

                        allowed_invoice_types = (
                            move._is_in()
                            and ("in_invoice", "out_refund")
                            or ("in_refund", "out_invoice")
                        )
                        if (
                            move
                            not in move._get_related_invoices()
                            .filtered(lambda x: x.type in allowed_invoice_types)
                            ._get_last_step_stock_moves()
                            and move.picking_id.purchase_id
                        ):
                            account_id = accounts[move.product_id.product_tmpl_id.id][
                                "stock_input"
                            ].id
                    else:
                        account_id = accounts[move.product_id.product_tmpl_id.id][
                            "expense"
                        ].id

                    if hasattr(move, "operating_unit_id"):
                        move = move.with_context(
                            operating_unit_id=move.operating_unit_id.id
                        )
                    move.with_context(
                        force_valuation_amount=-correction_value,
                        forced_quantity=0,
                        reforce_ref=True,
                        force_period_date=wizard.accounting_date,
                        force_company=wizard.company_id.id,
                    )._create_account_move_line(account_id, acc_valuation, journal_id)
        return {"type": "ir.actions.act_window_close"}


class StockFifoChangeStandardPriceLine(models.TransientModel):
    _name = "stock.fifo.change_standard_price.line"
    _description = "Update FIFO Product Line"
    _rec_name = "move_id"

    def _compute_lots(self):
        for record in self:
            record.lot_ids = record.mapped("move_id.move_line_ids.lot_id")

    wizard_id = fields.Many2one(
        comodel_name="stock.fifo.change_standard_price", required=True
    )
    move_id = fields.Many2one("stock.move", readonly=True)
    date = fields.Datetime(related="move_id.date", readonly=True)
    location_id = fields.Many2one(
        "stock.location",
        related="move_id.location_dest_id",
        readonly=True,
        string="Location",
    )
    product_id = fields.Many2one(
        comodel_name="product.product", related="move_id.product_id", readonly=True
    )
    lot_ids = fields.Many2many(
        comodel_name="stock.production.lot", compute="_compute_lots"
    )
    old_cost = fields.Float(
        digits=dp.get_precision("Product Price"), related="move_id.price_unit"
    )
    remaining_qty = fields.Float(related="move_id.remaining_qty", readonly=True)
    remaining_value = fields.Float(related="move_id.remaining_value", readonly=True)
    value = fields.Float(related="move_id.value", readonly=True)
    new_cost = fields.Float(digits=dp.get_precision("Product Price"))
