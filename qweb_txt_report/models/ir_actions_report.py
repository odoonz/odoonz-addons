# Copyright 2017 Open For Small Business Ltd
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'

    report_type = fields.Selection(selection_add=[('qweb-text', 'Text')])

    def render_qweb_text(self, docids, data=None):
        """
        Note the encoding context key must be a tuple or list of args to
        send to decode
        """
        res = self.render_qweb_html(docids, data=data)[0]
        if 'encoding' in self._context:
            res.decode('utf-8').encode(*self._context['encoding'])
        return res, 'txt'

    @api.model
    def _get_report_from_name(self, report_name):
        """Get the first record of ir.actions.report having the ``report_name``
        as value for the field report_name.
        """
        res = super()._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report']
        conditions = [('report_type', '=', 'qweb-text'),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
