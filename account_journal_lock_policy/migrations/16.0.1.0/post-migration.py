from openupgrade import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    where_clause = f" WHERE {openupgrade.get_legacy_name('enforce_lock')} IS TRUE"
    openupgrade.logged_query(
        env.cr,
        "UPDATE account_journal SET enforce_lock = 'policy'" + where_clause
    )
