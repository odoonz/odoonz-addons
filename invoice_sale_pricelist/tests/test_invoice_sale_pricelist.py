# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare as fc, mute_logger


class TestSale(TransactionCase):
    @mute_logger("odoo.addons.base.ir.ir_model", "odoo.osv.orm")
    def setUp(self):
        super(TestSale, self).setUp()
        context_no_mail = {
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nolog": True,
            "no_reset_password": True,
        }
        self.datacard = self.env.ref("product.product_delivery_02")
        self.usb_adapter = self.env.ref("product.product_delivery_01")
        self.uom_ton = self.env.ref("uom.product_uom_ton")
        self.uom_unit_id = self.ref("uom.product_uom_unit")
        self.uom_dozen_id = self.ref("uom.product_uom_dozen")
        self.uom_kgm_id = self.ref("uom.product_uom_kgm")

        self.public_pricelist = self.env.ref("product.list0")
        self.sale_pricelist_id = self.env["product.pricelist"].create(
            {
                "name": "Sale pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "compute_price": "formula",
                            "base": "list_price",  # based on public price
                            "price_discount": 10,
                            "product_id": self.usb_adapter.id,
                            "applied_on": "0_product_variant",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "compute_price": "formula",
                            "base": "list_price",  # based on public price
                            "price_surcharge": -0.5,
                            "product_id": self.datacard.id,
                            "applied_on": "0_product_variant",
                        },
                    ),
                ],
            }
        )
        IrModelData = self.env["ir.model.data"].with_context(context_no_mail)
        account_obj = self.env["account.account"].with_context(context_no_mail)
        sale_obj = self.env["sale.order"].with_context(context_no_mail)

        user_type_id = IrModelData.xmlid_to_res_id("account.data_account_type_revenue")
        account_rev_id = account_obj.create(
            {
                "code": "X2020",
                "name": "Sales - Test Sales Account",
                "user_type_id": user_type_id,
                "reconcile": True,
            }
        )

        partner = self.env.ref("base.res_partner_2")

        product_template_id = self.env.ref("sale.advance_product_0").product_tmpl_id
        product_template_id.write({"property_account_income_id": account_rev_id})
        p = self.usb_adapter
        order = sale_obj.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "date_order": datetime.today(),
                "pricelist_id": self.sale_pricelist_id.id,
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
                ],
            }
        )

        context = {
            "active_model": "sale.order",
            "active_ids": [order.id],
            "active_id": order.id,
        }
        order.with_context(**context).action_confirm()
        payment = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "amount": 5,
                "fixed_amount": 5,
                "product_id": self.env.ref("sale.advance_product_0").id,
            }
        )
        payment.with_context(context).create_invoices()
        self.invoice = order.invoice_ids[0]
        self.sale_line = order.order_line[0]

    def test_sale_invoice_pricelist(self):
        expected_price_unit = self.usb_adapter.with_context(
            pricelist=self.sale_pricelist_id.id
        ).price
        ail = self.env["account.move.line"].new(
            {
                "move_id": self.invoice.id,
                "product_id": self.usb_adapter.id,
                "quantity": 1.0,
                "product_uom_id": self.uom_unit_id,
            }
        )
        ail.sale_line_ids |= self.sale_line
        ail._onchange_product_id()
        self.assertFalse(fc(expected_price_unit, ail.price_unit, 2))

    def test_sale_invoice_partner(self):
        partner = self.env.ref("base.res_partner_2")
        partner.property_product_pricelist = self.sale_pricelist_id
        expected_price_unit = self.usb_adapter.with_context(
            pricelist=self.sale_pricelist_id.id
        ).price
        ail = self.env["account.move.line"].new(
            {
                "move_id": self.invoice.id,
                "product_id": self.usb_adapter.id,
                "quantity": 1.0,
                "product_uom_id": self.uom_unit_id,
            }
        )
        ail._onchange_product_id()
        self.assertFalse(fc(expected_price_unit, ail.price_unit, 2))
