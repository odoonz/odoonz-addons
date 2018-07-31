# -*- coding: utf-8 -*-
# Copyright 2018 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    signature_logo = fields.Binary(attachment=True)
