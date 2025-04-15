from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_pricelist_assortment_item pip
        SET display_applied_on = applied_on
        WHERE applied_on = '2_product_category'
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_pricelist_assortment_item pip
        SET display_applied_on = '1_product'
        WHERE applied_on != '2_product_category'
        """,
    )
