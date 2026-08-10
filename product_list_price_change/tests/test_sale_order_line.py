# Copyright 2026 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestSaleOrderLinePartnerPriceContext(TransactionCase):
    """``sale.order.line._get_product_price_context()`` must inject
    ``partner_id`` so that a customer-specific implementation delay on a
    price change actually affects the price used on a quotation/sale order
    line (see ``models/sale_order_line.py``).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delayed_category = cls.env["res.partner.category"].create(
            {"name": "SOL Delayed Pricing Category"}
        )
        cls.delayed_partner = cls.env["res.partner"].create(
            {
                "name": "SOL Delayed Pricing Partner",
                "category_id": [Command.link(cls.delayed_category.id)],
            }
        )
        cls.regular_partner = cls.env["res.partner"].create(
            {"name": "SOL Regular Partner"}
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {"name": "SOL Partner Cache Test Product", "list_price": 50.0}
        )
        cls.product = cls.product_tmpl.product_variant_ids[0]

        cls.price_change = cls.env["product.price.change"].create(
            {
                "name": "SOL Partner Cache Test Change",
                "effective_date": fields.Date.today() - timedelta(days=1),
                "state": "live",
                "product_line_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": cls.product_tmpl.id,
                            "list_price": 10.0,
                        }
                    )
                ],
            }
        )
        cls.env["product.price.change.implementation_delay"].create(
            {
                "name": "SOL delay for tagged category",
                "effective_date": fields.Date.today() + timedelta(days=1),
                "price_change_id": cls.price_change.id,
                "included_categories": [Command.link(cls.delayed_category.id)],
            }
        )

    def _create_line(self, partner):
        order = self.env["sale.order"].create({"partner_id": partner.id})
        return self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
            }
        )

    def test_product_price_context_includes_partner(self):
        line = self._create_line(self.delayed_partner)
        self.assertEqual(
            line._get_product_price_context().get("partner_id"),
            self.delayed_partner.id,
        )

    def test_delayed_partner_still_sees_old_price_on_new_quotation(self):
        line = self._create_line(self.delayed_partner)
        self.assertEqual(line._get_pricelist_price(), 50.0)
        self.assertEqual(line.price_unit, 50.0)

    def test_regular_partner_sees_new_price_on_new_quotation(self):
        line = self._create_line(self.regular_partner)
        self.assertEqual(line._get_pricelist_price(), 10.0)
        self.assertEqual(line.price_unit, 10.0)
