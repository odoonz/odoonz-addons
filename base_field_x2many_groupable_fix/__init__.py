from odoo import fields

# x2many fields are never sortable or groupable. The base Field class
# falls back to _read_group_groupby / _order_field_to_sql on the comodel,
# which is catastrophically slow on large tables (e.g. ir.attachment).
#
# Upstream only fixed the inherited-field case:
# https://github.com/odoo/odoo/commit/68e7555
#
# Remove this module once Odoo adds the x2many short-circuit to core.
fields.One2many._description_sortable = lambda self, env: False
fields.One2many._description_groupable = lambda self, env: False
fields.Many2many._description_sortable = lambda self, env: False
fields.Many2many._description_groupable = lambda self, env: False
