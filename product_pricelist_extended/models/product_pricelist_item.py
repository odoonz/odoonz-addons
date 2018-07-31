# Copyright 2014- Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ProductPricelistItem(models.Model):
    """product pricelist item - little changes to enable m2m product_ids"""
    _inherit = 'product.pricelist.item'
    _order = "applied_on, min_quantity desc, categ_id desc, name, id"

    product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='pricelist_item_product_rel',
        column1='pricelist_item_id',
        column2='prod_id',
        string='Products',
    )
    product_tmpl_ids = fields.Many2many(
        comodel_name='product.template',
        relation='pricelist_item_tmpl_rel',
        column1='pricelist_item_id',
        column2='tmpl_id',
        string='Templates',
        oldname='tmpl_ids',
    )
    price_categ_id = fields.Many2one(
        comodel_name='product.price.category',
        string='Pricing Category',
        oldname='price_categ'
    )

    code_inclusion = fields.Char('Code includes')
    code_exclusion = fields.Char('Code excludes')

    # Inherits upstream usage of deprecated api.one
    # pylint: disable=W8104
    @api.one
    @api.depends('price_categ_id', 'product_tmpl_ids', 'product_ids')
    def _get_pricelist_item_name_price(self):
        super()._get_pricelist_item_name_price()
        if self.price_categ_id:
            self.name = _("Price Category: %s") % self.price_categ_id.name
        elif self.product_tmpl_ids:
            self.name = ','.join(self.product_tmpl_ids.mapped('name'))
        elif self.product_ids:
            self.name = ','.join(
                [p.display_name.replace('[%s]' % p.code, '')
                 for p in self.product_ids])
        suffix = []
        if self.code_inclusion:
            suffix.append(_('contains %s') % self.code_inclusion)
        if self.code_exclusion:
            suffix.append(_('excludes %s') % self.code_exclusion)
        if suffix:
            self.name = self.name + _('(Code %s)') % ', '.join(suffix)
