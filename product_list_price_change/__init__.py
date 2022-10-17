from . import models
from . import wizards


from odoo.api import Environment, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    res_ids = (
        env["ir.model.data"]
        .search([("model", "=", "ir.ui.menu"), ("module", "=", "sale")])
        .mapped("res_id")
    )
    env["ir.ui.menu"].browse(res_ids).update({"active": False})


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    cr.execute("""SELECT id, list_price FROM product_template""")
    cr.fetchall()
    res_ids = (
        env["ir.model.data"]
        .search([("model", "=", "ir.ui.menu"), ("module", "=", "sale")])
        .mapped("res_id")
    )
    env["ir.ui.menu"].browse(res_ids).update({"active": True})
