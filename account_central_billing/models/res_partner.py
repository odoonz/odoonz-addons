# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """inherit base.res_partner and add columns to allow central invoicing"""
    _inherit = 'res.partner'

    invoicing_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Invoicing Customer',
    )
    store_ref = fields.Char(
        string='Store Code',
        help='If the customer requires specific store '
             'references on documentation',
        copy=False
    )
    billing_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Billing Supplier',
        oldname='hq_partner_id'
    )

    store_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='invoicing_partner_id',
        string='Stores',
        copy=False
    )

    @api.constrains('store_ref', 'invoicing_partner_id')
    def _check_store_code(self):
        """This function checks that the store code is unique within
        the account hierarchy it belongs"""
        if not self.invoicing_partner_id:
            return True
        for p in self:
            store_refs = p.invoicing_partner_id.store_ids.filtered(
                lambda r: bool(r.store_ref)).mapped('store_ref')
            if len(store_refs) != len(set(store_refs)):
                raise ValidationError('Cannot have duplicate store codes')

    @api.multi
    def get_billing_partner(self, vals, invoice=None):

        self.ensure_one()

        invoice_type = vals.get('type',
                                invoice.type if invoice else
                                self._context.get('type', 'out_invoice'))
        if invoice_type.startswith('out_'):
            f = 'invoicing_partner_id'
        elif invoice_type.startswith('in_'):
            f = 'billing_partner_id'

        if 'company_id' in vals:
            invoice_company = self.env['res.company'].browse(
                vals['company_id'])
        elif invoice:
            invoice_company = invoice.company_id
        else:
            invoice_company = self.env['res.company']._company_default_get(
                'account.invoice')
        company_partner = invoice_company.partner_id
        p = self
        while p[f]:
                if p[f] == company_partner:
                    break
                p = p[f]
        return p.id
