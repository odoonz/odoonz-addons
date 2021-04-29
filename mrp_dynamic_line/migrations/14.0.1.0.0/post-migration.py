def migrate(cr, version):
    cr.execute("UPDATE mrp_bom_line SET product_id=variant_id;")
