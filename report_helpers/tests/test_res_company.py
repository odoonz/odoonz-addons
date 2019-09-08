# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")

    def test_report_addresses(self):
        inv_partner = self.env["res.partner"].create(
            {
                "type": "invoice",
                "parent_id": self.company.partner_id.id,
                "name": "invoice",
            }
        )
        del_partner = self.env["res.partner"].create(
            {
                "type": "delivery",
                "parent_id": self.company.partner_id.id,
                "name": "delivery",
            }
        )
        self.assertEqual(self.company.postal_address_id, inv_partner)
        self.assertEqual(self.company.physical_address_id, del_partner)
