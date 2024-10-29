# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestTaxFromAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_sale_order = cls.env.ref("sale.sale_order_1")
        cls.test_purchase_order = cls.env.ref("purchase.purchase_order_1")

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
        cls.test_company = cls.env["res.company"].create({"name": "Test Company"})
        cls.env["account.chart.template"].try_loading(
            "generic_coa", cls.test_company, install_demo=False
        )

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
        cls.test_fpos_tax1 = cls.env["account.fiscal.position.tax"].create(
            {
                "tax_src_id": cls.test_tax_sale1.id,
                "tax_dest_id": cls.test_default_sale_tax.id,
                "position_id": cls.test_fpos_so.id,
            }
        )
        cls.test_fpos_tax2 = cls.env["account.fiscal.position.tax"].create(
            {
                "tax_src_id": cls.test_tax_purch1.id,
                "tax_dest_id": cls.test_default_purch_tax.id,
                "position_id": cls.test_fpos_po.id,
            }
        )
        cls.test_vender = cls.env.ref("product.product_supplierinfo_1")
        cls.test_product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "taxes_id": False,
                "supplier_taxes_id": False,
                "seller_ids": cls.test_vender,
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

    def test_check_tax_id_in_so_line(self):
        self.test_sale_order.fiscal_position_id = False
        so_line_1 = self.test_sale_order.order_line[0]
        so_line_1.product_id.taxes_id = False
        so_line_1.product_id.product_tmpl_id.get_product_accounts()[
            "income"
        ].tax_ids = False

        # Test company.account_sale_tax_id
        so_line_1.company_id.account_sale_tax_id = self.test_default_sale_tax
        tax_id = so_line_1._get_default_taxes()
        self.assertEqual(tax_id, self.test_default_sale_tax)

        # Test product.taxes_id
        so_line_1.product_id.taxes_id = self.test_tax_sale1
        tax_id = so_line_1._get_default_taxes()
        self.assertEqual(tax_id, self.test_tax_sale1)

        # Test fpos
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

        # Test company.account_sale_tax_id
        order_line_2.company_id.account_purchase_tax_id = self.test_default_purch_tax
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_default_purch_tax)

        # Test account tax_id
        order_line_2.product_id.product_tmpl_id.get_product_accounts()[
            "expense"
        ].tax_ids = self.test_tax_purch2
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_tax_purch2)

        # Test product.taxes_id
        order_line_2.product_id.supplier_taxes_id = self.test_tax_purch1
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_tax_purch1)

        # Test fpos
        self.test_purchase_order.fiscal_position_id = self.test_fpos_po
        tax_id = order_line_2._get_default_taxes("in_invoice")
        self.assertEqual(tax_id, self.test_default_purch_tax)

    def test_product_tax_in_multi_companies(self):
        # use same product, create a new sale order line
        # in an existing sale order: order line should have
        # tax_id = company.account_sale_tax_id
        self.test_sale_order.company_id.account_sale_tax_id = self.test_default_sale_tax
        so = Form(self.test_sale_order)
        with so.order_line.new() as line_a:
            line_a.name = "In company A"
            line_a.product_id = self.test_product
        so = so.save()

        line_a = so.order_line.search([("product_id", "=", self.test_product.id)])
        self.assertEqual(
            line_a.tax_id,
            so.company_id.account_sale_tax_id,
            "Line A should have same tax as so's company tax_id",
        )

        # use same product, create a sale order line
        # in an new sale order in different company(company2):
        # order line should have tax_id = company.account_sale_tax_id
        so_new = Form(self.env["sale.order"])
        so_new.partner_id = self.env.ref("base.res_partner_2")
        so_new.company_id = self.test_company
        with so_new.order_line.new() as line_b:
            line_b.name = "In company B"
            line_b.product_id = self.test_product

        so_new = so_new.save()
        line_b = so_new.order_line
        self.assertEqual(
            line_b.tax_id,
            so_new.company_id.account_sale_tax_id,
            "Line B should have same tax as so_new's company tax_id",
        )

        # assign a new taxes_id(in company2) to the same product,
        # recreate the order line in the new order and
        # it should have: tax_id = product.taxes_id
        self.test_product.taxes_id = self.test_tax_sale_comp2
        with Form(so_new) as so_new:
            so_new.order_line.remove(index=0)
            with so_new.order_line.new() as line_b1:
                line_b1.name = "In company B: add product taxes_id"
                line_b1.product_id = self.test_product
        so_new = so_new.save()
        line_b1 = so_new.order_line
        self.assertEqual(
            line_b1.tax_id,
            line_b1.product_id.taxes_id,
            "Line B1 should have same tax as product's taxes_id",
        )

        # recreate the order line in the existing order
        # and its tax_id should be same as from company A
        with Form(so) as so:
            so.order_line.remove(index=len(so.order_line) - 1)
            with so.order_line.new() as line_a1:
                line_a1.name = "In company A: check line.tax_id"
                line_a1.product_id = self.test_product
        so = so.save()
        line_a1 = so.order_line[-1]
        self.assertEqual(
            line_a1.tax_id,
            so.company_id.account_sale_tax_id,
            "Line A1 should stay the same",
        )
