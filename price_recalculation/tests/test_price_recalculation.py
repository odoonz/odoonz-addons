import logging
from odoo.addons.sale.tests.test_sale_common import TestSale
import mock


_logger = logging.Logger(__name__)

wizard = (
    "odoo.addons.price_recalculation.wizards.price_recalculation.PriceRecalculation"
)


class TestPriceCalculation(TestSale):
    def setUp(self):
        """Initial Setup"""
        super().setUp()
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for p in self.products.values()
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

    def test_defaults(self):
        with mock.patch("%s._get_lines" % wizard) as get_lines:
            get_lines.return_value = []
            flds = (
                self.env["price.recalculation"]
                .with_context(active_ids=[self.so.id], active_model="sale.order")
                .default_get(["name", "partner_id", "line_ids", "date_order"])
            )
        self.assertEqual(flds["name"], self.so.id)
        self.assertEqual(flds["partner_id"], self.so.partner_id.id)
        self.assertEqual(flds["date_order"], self.so.date_order)
