# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """inherit base.res_partner and add columns to allow central invoicing"""
    _inherit = "res.partner"

    invoicing_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Invoicing Customer"
    )
    store_ref = fields.Char(
        string="Store Code",
        help="If the customer requires specific store "
        "references on documentation",
        copy=False,
    )
    billing_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Billing Supplier",
        oldname="hq_partner_id",
    )

    store_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="invoicing_partner_id",
        string="Stores",
        copy=False,
    )

    @api.constrains("store_ref", "invoicing_partner_id")
    def _check_store_code(self):
        """This function checks that the store code is unique within
        the account hierarchy it belongs"""
        if not self.invoicing_partner_id:
            return True
        for partner in self:
            store_refs = partner.invoicing_partner_id.store_ids.filtered(
                lambda r: bool(r.store_ref)
            ).mapped("store_ref")
            if len(store_refs) != len(set(store_refs)):
                raise ValidationError(_("Cannot have duplicate store codes"))

    @api.multi
    def get_billing_partner(self, vals, invoice=None):

        self.ensure_one()

        invoice_type = vals.get(
            "type",
            invoice.type
            if invoice
            else self._context.get("type", "out_invoice"),
        )
        if invoice_type.startswith("out_"):
            field = "invoicing_partner_id"
        elif invoice_type.startswith("in_"):
            field = "billing_partner_id"

        if "company_id" in vals:
            invoice_company = self.env["res.company"].browse(vals["company_id"])
        elif invoice:
            invoice_company = invoice.company_id
        else:
            invoice_company = self.env["res.company"]._company_default_get(
                "account.invoice"
            )
        company_partner = invoice_company.partner_id
        partner = self
        while partner[field]:
            if partner[field] == company_partner:
                break
            partner = partner[field]
        return partner.id
