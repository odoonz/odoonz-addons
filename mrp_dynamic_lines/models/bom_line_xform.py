# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BomLineXform(models.Model):
    """Bom Line Dynamic Transformations"""
    _name = 'bom.line.xform'
    _description = __doc__

    name = fields.Char()
    technical_name = fields.Char(
        help="Will correspond to a function e.g. match_attributes"
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text()
    sequence = fields.Integer(default=5)
    application_point = fields.Selection([('explode', 'BoM Explosion'),
                                          ('move', 'Raw Move Generation')])

    bom_line_ids = fields.Many2many('mrp.bom.line')

    @api.multi
    @api.onchange('product_tmpl_id', 'variant_id')
    @api.depends('product_tmpl_id', 'variant_id')
    def _compute_product_id(self):
        Product = self.env['product.product']
        for bom_line in self:
            if bom_line._context.get('product_id'):
                parent_product = Product.browse(
                    [bom_line._context.get('product_id')])
                bom_tmpl = bom_line.product_tmpl_id
                # We only want variants of the template
                search_domain = [('product_tmpl_id', '=', bom_tmpl.id)]
                # that have the required values
                if bom_line.required_value_ids:
                    for value in bom_line.required_value_ids:
                        search_domain.append(
                            ('attribute_value_ids', 'in', [value.id])
                        )
                # and share values with the parent product
                common_attrs = self.env['product.attribute']
                if bom_line.match_attributes:
                    parent_attrs = parent_product.attribute_value_ids.mapped(
                        'attribute_id')
                    bom_attrs = bom_tmpl.attribute_line_ids.mapped(
                        'attribute_id')
                    common_attrs = parent_attrs & bom_attrs
                    return_default = False
                else:
                    return_default = True
                if common_attrs:
                    value_ids = [v.id for v in
                                 parent_product.attribute_value_ids if
                                 v.attribute_id.id in set(common_attrs.ids)]
                    for value_id in value_ids:
                        search_domain.append(
                            ('attribute_value_ids', 'in', [value_id])
                        )
                # and there can be only one result
                products = Product.search(search_domain)
                if len(products) == 1:
                    bom_line.product_id = products[0]
                elif return_default or not products:
                    bom_line.product_id = bom_line.variant_id
                else:
                    names = ['  - %s' % p['name'] for p in products.name_get()]
                    raise ValidationError(
                        _('The BoM Line %s in BoM %s is matching too many '
                          'products.  Expected < 1 and received:\n%s') %
                        (self.product_tmpl_id.name,
                         self.bom_id.name, '\n'.join(names)))
            else:
                bom_line.product_id = bom_line.variant_id

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.variant_id = False
