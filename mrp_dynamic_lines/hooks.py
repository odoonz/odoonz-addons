# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists, create_column


def pre_init_hook(cr):
    for field in ["variant_id", "product_tmpl_id"]:
        if not column_exists(cr, "mrp_bom_line", field):
            create_column(cr, "mrp_bom_line", field, "INT")
    cr.execute(
        "UPDATE mrp_bom_line "
        "SET variant_id=product_id,"
        "product_tmpl_id=p.product_tmpl_id "
        "FROM product_product p WHERE p.id=product_id"
    )
    return True


def uninstall_hook(cr, pool):
    cr.execute("UPDATE mrp_bom_line SET product_id=variant_id;")
    return True
