# -*- coding: utf-8 -*-
# Copyright 2018 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @api.multi
    def create_variant_ids(self):
        with self.env.norecompute():
            super().create_variant_ids()
        self.recompute()
