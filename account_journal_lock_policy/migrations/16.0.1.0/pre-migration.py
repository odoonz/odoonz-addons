from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, {'account.journal': ['enforce_lock']})
