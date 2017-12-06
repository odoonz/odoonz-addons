# -*- coding: utf-8 -*-
# Copyright 2017 Open For Small Business Ltd
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_operating_unit = False

    def set_context(self, options):
        """This method will set information inside the context based on the
        options dict as some options need to be in context for the query_get
        method defined in account_move_line"""
        ctx = super(AccountReport, self).set_context(options)
        if options.get('operating_unit'):
            ou_ids = [ou.get('id') for ou in options['operating_unit']
                      if ou.get('selected')]
            ctx['operating_unit_ids'] = ou_ids
        return ctx

    def _build_options(self, previous_options=None):
        options = super(AccountReport, self)._build_options(
            previous_options=previous_options)
        if not options['operating_unit']:
            options['operating_unit'] = [{
                'id': ou.id,
                'name': ou.name,
                'selected': (
                    True if ou.id == self.env.user.default_operating_unit_id.id
                    else False)
            } for ou in self.env.user.operating_unit_ids]
        return options
