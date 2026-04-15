# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestTaxFromAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Tax Test Partner", "is_company": True}
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "Tax Test Partner B", "is_company": True}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Tax Test Product",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 50.0,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Tax Test Product B",
                "type": "consu",
                "list_price": 200.0,
                "standard_price": 80.0,
            }
        )

        cls.test_default_sale_tax = cls.env["account.tax"].create(
            {
                "name": "Test 15%",
                "type_tax_use": "sale",
                "amount": 15.0,
                "amount_type": "percent",
            }
        )
        cls.test_default_purch_tax = cls.env["account.tax"].create(
            {
                "name": "Test 15%",
                "type_tax_use": "purchase",
                "amount": 15.0,
                "amount_type": "percent",
            }
        )
        cls.test_tax_sale1 = cls.env["account.tax"].create(
            {
                "name": "Test 20%",
                "type_tax_use": "sale",
                "amount": 20.0,
                "amount_type": "percent",
            }
        )
        cls.test_company = cls.env.company

        cls.test_tax_sale2 = cls.env["account.tax"].create(
            {
                "name": "Test 30% (S)",
                "type_tax_use": "sale",
                "amount": 30.0,
                "amount_type": "percent",
                "company_id": cls.test_company.id,
            }
        )
        cls.test_company.account_sale_tax_id = cls.test_tax_sale2

        cls.test_tax_purch1 = cls.env["account.tax"].create(
            {
                "name": "Test 20% (S)",
                "type_tax_use": "purchase",
                "amount": 20.0,
                "amount_type": "percent",
            }
        )
        cls.test_tax_purch2 = cls.env["account.tax"].create(
            {
                "name": "Test 30% (P)",
                "type_tax_use": "purchase",
                "amount": 30.0,
                "amount_type": "percent",
            }
        )

        cls.test_product = cls.env["product.product"].create(
            {
                "name": "Test Product No Tax",
                "taxes_id": False,
                "supplier_taxes_id": False,
            }
        )

        cls.test_tax_sale_comp2 = cls.env["account.tax"].create(
            {
                "name": "Test 30%",
                "type_tax_use": "sale",
                "amount": 30.0,
                "amount_type": "percent",
                "company_id": cls.test_company.id,
            }
        )

        so_vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": cls.product.id,
                        "product_uom_qty": 5.0,
                        "price_unit": 100.0,
                    }
                ),
                Command.create(
                    {
                        "product_id": cls.product_b.id,
                        "product_uom_qty": 3.0,
                        "price_unit": 200.0,
                    }
                ),
            ],
        }
        if "dispatch_method" in cls.env["sale.order"]._fields:
            so_vals["dispatch_method"] = "yard"
        cls.test_sale_order = cls.env["sale.order"].create(so_vals)

        cls.test_purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 50.0,
                        }
                    ),
                ],
            }
        )

        cls.test_fpos_so = cls.env["account.fiscal.position"].create(
            {
                "name": "Sale Tax Mapping",
                "company_id": cls.test_sale_order.company_id.id,
            }
        )
        cls.test_fpos_po = cls.env["account.fiscal.position"].create(
            {
                "name": "Purchase Tax Mapping",
                "company_id": cls.test_purchase_order.company_id.id,
            }
        )
        cls.test_default_sale_tax.write(
            {
                "fiscal_position_ids": [Command.link(cls.test_fpos_so.id)],
                "original_tax_ids": [Command.link(cls.test_tax_sale1.id)],
            }
        )
        cls.test_default_purch_tax.write(
            {
                "fiscal_position_ids": [Command.link(cls.test_fpos_po.id)],
                "original_tax_ids": [Command.link(cls.test_tax_purch1.id)],
            }
        )

    def test_check_tax_id_in_so_line(self):
        self.test_sale_order.fiscal_position_id = False
        so_line_1 = self.test_sale_order.order_line[0]
        so_line_1.product_id.taxes_id = False
        so_line_1.product_id.product_tmpl_id.get_product_accounts()[
            "income"
        ].tax_ids = False

        so_line_1.company_id.account_sale_tax_id = self.test_default_sale_tax
        tax_id = so_line_1._get_default_taxes()
        self.assertEqual(tax_id, self.test_default_sale_tax)

        so_line_1.product_id.taxes_id = self.test_tax_sale1
        tax_id = so_line_1._get_default_taxes()
        self.assertEqual(tax_id, self.test_tax_sale1)

        self.test_sale_order.fiscal_position_id = self.test_fpos_so
        tax_id = so_line_1._get_default_taxes()
        self.assertEqual(tax_id, self.test_default_sale_tax)

    def test_check_tax_id_in_po_line(self):
        self.test_purchase_order.fiscal_position_id = False
        order_line_2 = self.test_purchase_order.order_line[0]
        order_line_2.product_id.supplier_taxes_id = False
        order_line_2.product_id.product_tmpl_id.get_product_accounts()[
            "expense"
        ].tax_ids = False

        order_line_2.company_id.account_purchase_tax_id = self.test_default_purch_tax
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_default_purch_tax)

        order_line_2.product_id.product_tmpl_id.get_product_accounts()[
            "expense"
        ].tax_ids = self.test_tax_purch2
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_tax_purch2)

        order_line_2.product_id.supplier_taxes_id = self.test_tax_purch1
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_tax_purch1)

        self.test_purchase_order.fiscal_position_id = self.test_fpos_po
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_default_purch_tax)

    def test_product_tax_in_multi_companies(self):
        self.test_sale_order.company_id.account_sale_tax_id = self.test_default_sale_tax
        so = Form(self.test_sale_order)
        if not so.client_order_ref:
            so.client_order_ref = "TEST-MULTI-CO"
        with so.order_line.new() as line_a:
            line_a.name = "In company A"
            line_a.product_id = self.test_product
        so = so.save()

        line_a = so.order_line.search([("product_id", "=", self.test_product.id)])
        self.assertEqual(
            line_a.tax_ids,
            so.company_id.account_sale_tax_id,
            "Line A should have same tax as so's company tax_id",
        )

        so_new_vals = {
            "partner_id": self.partner_b.id,
            "company_id": self.test_company.id,
            "client_order_ref": "TEST-MULTI-CO-B",
            "order_line": [
                Command.create(
                    {
                        "name": "In company B",
                        "product_id": self.test_product.id,
                        "product_uom_qty": 1.0,
                        "price_unit": 100.0,
                    }
                ),
            ],
        }
        if "dispatch_method" in self.env["sale.order"]._fields:
            so_new_vals["dispatch_method"] = "yard"
        so_new = self.env["sale.order"].create(so_new_vals)
        line_b = so_new.order_line
        self.assertEqual(
            line_b.tax_ids,
            so_new.company_id.account_sale_tax_id,
            "Line B should have same tax as so_new's company tax_id",
        )

        self.test_product.taxes_id = self.test_tax_sale_comp2
        with Form(so_new) as so_new:
            so_new.order_line.remove(index=0)
            with so_new.order_line.new() as line_b1:
                line_b1.name = "In company B: add product taxes_id"
                line_b1.product_id = self.test_product
        so_new = so_new.save()
        line_b1 = so_new.order_line
        self.assertEqual(
            line_b1.tax_ids,
            line_b1.product_id.taxes_id,
            "Line B1 should have same tax as product's taxes_id",
        )

        with Form(so) as so:
            so.order_line.remove(index=len(so.order_line) - 1)
            with so.order_line.new() as line_a1:
                line_a1.name = "In company A: check line.tax_ids"
                line_a1.product_id = self.test_product
        so = so.save()
        line_a1 = so.order_line[-1]
        self.assertEqual(
            line_a1.tax_ids,
            line_a1.product_id.taxes_id or so.company_id.account_sale_tax_id,
        )
