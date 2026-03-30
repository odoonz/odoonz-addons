from odoo import fields

# The base Field._description_groupable / _description_sortable fall back to
# _read_group_groupby / _order_field_to_sql on the comodel, which is
# catastrophically slow on large tables (e.g. ir.attachment) and can even OOM.
#
# Upstream only fixed the inherited-field case:
# https://github.com/odoo/odoo/commit/68e7555
#
# Remove this module once Odoo adds x2many short-circuits to core.

# One2many: never groupable or sortable
fields.One2many._description_sortable = lambda self, env: False
fields.One2many._description_groupable = lambda self, env: False

# Many2many: groupable (used for tags etc.) but never sortable
fields.Many2many._description_sortable = lambda self, env: False
fields.Many2many._description_groupable = lambda self, env: True
