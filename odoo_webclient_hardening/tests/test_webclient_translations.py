# Copyright 2026 Graeme Gellatly
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.translate import code_translations

_MODULES = ["base", "web", "mail", "account", "sale"]


@tagged("post_install", "-at_install")
class TestWebclientTranslations(TransactionCase):
    def test_kept_modules_have_messages(self):
        """Every module returned carries at least one message."""
        translations, _lang_params = self.env[
            "ir.http"
        ]._get_translations_for_webclient(_MODULES, "en_US")
        self.assertTrue(
            all(data.get("messages") for data in translations.values()),
            "Modules with empty messages should be filtered out",
        )

    def test_dropped_modules_were_empty(self):
        """Any requested module that was dropped genuinely had no messages."""
        translations, _lang_params = self.env[
            "ir.http"
        ]._get_translations_for_webclient(_MODULES, "en_US")
        for module in _MODULES:
            if module not in translations:
                data = code_translations.get_web_translations(module, "en_US")
                self.assertFalse(
                    data.get("messages"),
                    f"{module} was dropped despite having messages",
                )
