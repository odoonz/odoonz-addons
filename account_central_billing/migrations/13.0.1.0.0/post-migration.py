from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        "UPDATE account_move "
        "SET order_partner_id=i.order_partner_id, order_invoice_id=i.order_invoice_id "
        "FROM account_invoice i WHERE i.move_id = account_move_id"
    )
