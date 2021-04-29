from openupgradelib import openupgrade

column_renames = {
    "bom_line_req_attr_val_rel": [
        ("product_attribute_value_id", "product_template_attribute_value_id")
    ]
}


def _migrate_attribute_values(env, version):
    env.cr.execute(
        """
    alter table bom_line_req_attr_val_rel drop constraint
    if exists bom_line_req_attr_val_rel_product_attribute_value_id_fkey;
    """
    )
    env.cr.execute(
        """
    SELECT ptav.id, r.mrp_bom_line_id, r.product_template_attribute_value_id
    from bom_line_req_attr_val_rel r,
    product_template_attribute_value ptav,
    product_template pt,
    mrp_bom_line bl
    WHERE pt.id=ptav.product_tmpl_id
    and r.mrp_bom_line_id = bl.id and pt.id=bl.product_tmpl_id
    and r.product_template_attribute_value_id=ptav.product_attribute_value_id
    """
    )
    res = env.cr.fetchall()
    for r in res:
        env.cr.execute(
            """
        UPDATE bom_line_req_attr_val_rel
        SET product_template_attribute_value_id = %s
        WHERE mrp_bom_line_id = %s and
        product_template_attribute_value_id=%s""",
            r,
        )
    # DELETE ANY INCOMPATIBLE ERRORS
    env.cr.execute(
        """
    SELECT r.mrp_bom_line_id, r.product_template_attribute_value_id
    from bom_line_req_attr_val_rel r;
    """
    )
    res = env.cr.fetchall()
    for r in res:
        env.cr.execute("SELECT product_tmpl_id FROM mrp_bom_line WHERE id=%s", (r[0],))
        p_id = env.cr.fetchall()[0]
        env.cr.execute(
            "SELECT id FROM product_template_attribute_value WHERE product_tmpl_id=%s",
            p_id,
        )
        ptav_ids = [x[0] for x in env.cr.fetchall()]
        if r[1] not in ptav_ids:
            env.cr.execute(
                """DELETE FROM bom_line_req_attr_val_rel WHERE mrp_bom_line_id=%s
                and product_template_attribute_value_id=%s""",
                r,
            )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "bom_line_req_attr_val_rel", "product_attribute_value_id"
    ):
        openupgrade.rename_columns(env.cr, column_renames)
    _migrate_attribute_values(env, version)
