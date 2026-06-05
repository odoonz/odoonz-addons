# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def _get_translations_for_webclient(self, modules, lang):
        """Drop modules that have no web (JS) translations from the payload.

        The public ``/web/webclient/translations`` endpoint otherwise returns
        an entry for every installed module, enumerating the full module
        footprint to unauthenticated callers. Modules without any messages
        contribute nothing usable (``_t`` falls back to the global table and
        then to the source string), so omitting them is transparent to the web
        client while removing the disclosure.
        """
        translations_per_module, lang_params = super()._get_translations_for_webclient(
            modules, lang
        )
        translations_per_module = {
            module: data
            for module, data in translations_per_module.items()
            if data and data.get("messages")
        }
        return translations_per_module, lang_params
