# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    """inherits account.account_invoice and adds the order_partner_id field
    as well as overriding ORM functions to ensure the parent partner and order
    partner are written and created correctly"""

    _inherit = "account.move"

    order_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Commercial Partner"
    )

    order_invoice_id = fields.Many2one(
        comodel_name="res.partner", string="Invoice Partner"
    )

    @api.constrains("partner_id", "order_partner_id")
    def _check_company(self):
        for record in self:
            if record.move_type != "entry" and record.company_id.partner_id.id in [
                record.partner_id.id,
                record.partner_id.commercial_partner_id.id,
            ]:
                raise ValidationError(_("Cannot self bill. %d") % record.id)

    @api.model_create_multi
    def create(self, vals_list):
        """Function overrides create to ensure that parent account is
        always used"""
        for vals in vals_list:
            if vals.get("partner_id"):
                vals.update(
                    self._get_central_billing_partner_vals(
                        vals["partner_id"],
                        vals["move_type"],
                        self._get_invoice_company(vals),
                    )
                )
        return super().create(vals_list)

    def write(self, vals):
        """Function overrides create to ensure that parent account is
        always used"""
        if vals.get("partner_id", False):
            company = self._get_invoice_company(vals)
            move_type = vals.get("move_type", self[0].move_type)
            vals.update(
                self._get_central_billing_partner_vals(
                    vals["partner_id"], move_type, company
                )
            )
        return super().write(vals)

    def _get_central_billing_partner_vals(self, partner_id, move_type, company):
        vals = {}
        if not partner_id:
            return vals
        partner = self.env["res.partner"].browse(partner_id).commercial_partner_id
        invoice_partner = partner._get_billing_partner(move_type, company)
        if invoice_partner != partner:
            vals.update(
                {
                    "partner_id": invoice_partner.id,
                    "order_partner_id": partner.id,
                    "order_invoice_id": partner_id,
                }
            )
        return vals

    @api.model
    def _search(self, args, **kwargs):
        """override search so we find subsidiary invoices when looking at
        that partner.
        """
        iter_args = list(args)
        args = []
        for arg in iter_args:
            if arg[0] == "partner_id" and arg[1] in ("=", "like", "ilike", "child_of"):
                args.extend(["|", arg, ("order_partner_id", arg[1], arg[2])])
            else:
                args.append(arg)
        return super()._search(args, **kwargs)

    def _get_refund_common_fields(self):
        return super()._get_refund_common_fields() + [
            "order_partner_id",
            "order_invoice_id",
        ]

    def _get_invoice_company(self, vals):
        if "company_id" in vals:
            invoice_company = self.env["res.company"].browse(vals["company_id"])
        elif "journal_id" in vals:
            invoice_company = (
                self.env["account.journal"].sudo().browse(vals["journal_id"]).company_id
            )
        elif self:
            invoice_company = self.company_id
        else:
            invoice_company = self.env.company
        return invoice_company
