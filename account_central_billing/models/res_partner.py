# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """inherit base.res_partner and add columns to allow central invoicing"""

    _inherit = "res.partner"

    invoicing_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Invoicing Customer"
    )
    store_ref = fields.Char(
        string="Store Code",
        help="If the customer requires specific store " "references on documentation",
        copy=False,
    )
    billing_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Billing Supplier"
    )

    store_ids = fields.One2many(
        comodel_name="res.partner",
        domain=[("is_company", "=", True), ("parent_id", "=", False)],
        inverse_name="invoicing_partner_id",
        string="Stores",
        copy=False,
    )

    @api.constrains("store_ref", "invoicing_partner_id")
    def _check_store_code(self):
        """This function checks that the store code is unique within
        the account hierarchy it belongs"""
        for partner in self.filtered(lambda r: bool(r.invoicing_partner_id)):
            store_refs = partner.invoicing_partner_id.store_ids.filtered(
                lambda r: bool(r.store_ref)
            ).mapped("store_ref")
            if len(store_refs) != len(set(store_refs)):
                raise ValidationError(_("Cannot have duplicate store codes"))

    def _get_out_billing_partner(self, company):
        self.ensure_one()
        partner = self._get_billing_partner("invoicing_partner_id", company)
        return partner._get_invoice_contact()

    def _get_in_billing_partner(self, company):
        self.ensure_one()
        partner = self._get_billing_partner("billing_partner_id", company)
        return partner._get_invoice_contact()

    def _get_billing_partner(self, fieldname, company):
        self.ensure_one()
        company_partner = company.partner_id
        partner = self
        while partner[fieldname]:
            if partner[fieldname] == company_partner:
                break
            partner = partner[fieldname]
        return partner

    def _get_invoice_contact(self):
        """Resolve the actual contact/address invoices should be sent to.

        `_get_billing_partner` only walks the central-billing chain to the
        right *account* (e.g. a customer's head office, or - absent any
        central billing setup - the customer's own commercial partner). It
        never looks at that account's designated Invoice Address, so
        invoices generated from it (e.g. via the recharge/onbehalf flows in
        `ril_intercompany_rules`) end up addressed to the bare company
        record instead of its invoice contact. `address_get` falls back to
        the partner itself when no dedicated invoice contact exists, so this
        is a no-op for accounts without one.
        """
        self.ensure_one()
        invoice_partner_id = self.address_get(["invoice"])["invoice"]
        return self.browse(invoice_partner_id)

    @api.model
    def _commercial_fields(self):
        """Returns the list of fields that are managed by the commercial entity
        to which a partner belongs. These fields are meant to be hidden on
        partners that aren't `commercial entities` themselves, and will be
        delegated to the parent `commercial entity`. The list is meant to be
        extended by inheriting classes."""
        return super()._commercial_fields() + [
            "invoicing_partner_id",
            "billing_partner_id",
        ]
