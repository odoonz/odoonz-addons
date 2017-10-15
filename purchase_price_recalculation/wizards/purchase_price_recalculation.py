# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PurchasePriceRecalculation(models.TransientModel):
    """Purchase Price Recalculation"""
    _inherit = ['price.recalculation']
    _name = 'purchase.price.recalculation'
    _description = __doc__

    name = fields.Many2one('purchase.order', 'Purchase Order')
    line_ids = fields.One2many('purchase.price.recalculation.line',
                               'price_recalculation_id', 'Lines')

    @staticmethod
    def _get_lines(purchase):

        def get_effective_tax_rate(line):
            if line.price_subtotal:
                return ((line.price_total - line.price_subtotal) /
                        line.price_subtotal)
            else:
                taxes = line.taxes_id.compute_all(
                    1, line.order_id.currency_id, 1.0, product=line.product_id,
                    partner=line.order_id.partner_id)
                return ((taxes['total_included'] - taxes['total_excluded']) /
                        taxes['total_excluded'])

        return [(0, 0, {
            'name': ol.id,
            'product_id': ol.product_id.id,
            'qty': ol.product_qty,
            'price_unit': ol.price_unit,
            'price_subtotal': ol.price_subtotal,
            'price_total': ol.price_total,
            'effective_tax_rate': get_effective_tax_rate(ol)
        }) for ol in purchase.order_line]

    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        return self.update_pricelist_lines(self.pricelist_id)

    @api.multi
    def _set_context(self):
        ctx = super(PurchasePriceRecalculation, self)._set_context()
        ctx.update({'warehouse_id': self.name.warehouse_id.id})
        return ctx

    @api.multi
    def _check_write_constraints(self):
        """
        Check write constraints for orders that can't be updated
        Note: Caller ensures one record
        """
        super(PurchasePriceRecalculation, self)._check_write_constraints()
        if self.name.picking_ids.filtered(lambda p: p.state == 'done'):
            raise ValidationError(
                _('You cannot change pricing on an order that has '
                  'already been received.'))

    @api.multi
    def action_write(self):
        self.ensure_one()
        self._check_write_constraints()
        order = self.name
        header_msgs = [_(u'<p><b>Pricing Updated</b></p>')]
        msgs = [u'<ul>']
        vals = {}
        if order.invoice_ids:
            msgs.append(_(u'<p><emph>The draft invoice has also '
                          u'been updated.</emph></p>'))
        vals.update(self._prepare_other_vals())
        order.write(vals)
        for line in self.line_ids:
            order_line = line.name
            if ((order_line.price_unit != line.price_unit) or
                    (line.name.discount != line.discount)):
                msgs.append(
                    _(u'<li>{0}: was ${1:.2f} ea - '
                      u'now ${2:.2f} ea</li>').format(
                        order_line.name,
                        order_line.price_subtotal/line.qty,
                        line.price_subtotal/line.qty))
                order_line.write({
                    'price_unit': line.price_unit,
                })
                order_line.invoice_lines.write({
                    'price_subtotal': line.price_subtotal,
                    'price_unit': line.price_unit,
                })
                order_line.move_ids.write(
                    {'price_unit': order_line._get_stock_move_price_unit()})
        if len(msgs) > 1:
                msgs.append(u'</ul><br/>')
        else:
            msgs = []
        order.invoice_ids.compute_taxes()
        msgs = header_msgs + msgs
        if msgs:
            body = ''.join(msgs)
            order.message_post(body=body)
        return {}
