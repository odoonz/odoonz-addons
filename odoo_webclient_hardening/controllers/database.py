# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from werkzeug.exceptions import NotFound

from odoo.http import route

from odoo.addons.web.controllers.database import Database


class DatabaseHardening(Database):
    """Disable the database *management* web endpoints.

    Databases here are never created, duplicated, dropped, backed up or
    restored through the web UI (that work goes through the shell / backup
    tooling). Those routes are ``auth="none"`` and gated only by the master
    password, i.e. an anonymous-reachable management/destruction surface, and
    the ``manager`` page is the UI that drives them.

    The read-only database ``selector`` (used to pick a database at login)
    and ``/web/database/list`` are deliberately left intact so multi-database
    login and listing keep working. Disabled routes return 404 so they appear
    absent rather than merely forbidden. ``**kw`` signatures ensure the 404 is
    returned regardless of which parameters a caller supplies.
    """

    @route()
    def manager(self, **kw):
        raise NotFound()

    @route()
    def create(self, **kw):
        raise NotFound()

    @route()
    def duplicate(self, **kw):
        raise NotFound()

    @route()
    def drop(self, **kw):
        raise NotFound()

    @route()
    def backup(self, **kw):
        raise NotFound()

    @route()
    def restore(self, **kw):
        raise NotFound()

    @route()
    def change_password(self, **kw):
        raise NotFound()
