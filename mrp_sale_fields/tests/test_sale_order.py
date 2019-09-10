# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, Form


class TestSaleOrder(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.categ_unit = self.env.ref('uom.product_uom_categ_unit')
        self.categ_kgm = self.env.ref('uom.product_uom_categ_kgm')
        self.warehouse = self.env.ref('stock.warehouse0')

    def test_00_sale_mrp_flow(self):
        """ Test sale to mrp flow with diffrent unit of measure."""
        def create_product(name, uom_id, routes=()):
            p = Form(self.env['product.product'])
            p.name = name
            p.type = 'product'
            p.uom_id = uom_id
            p.uom_po_id = uom_id
            p.route_ids.clear()
            for r in routes:
                p.route_ids.add(r)
            return p.save()

        self.uom_unit = self.env['uom.uom'].search([('category_id', '=', self.categ_unit.id), ('uom_type', '=', 'reference')], limit=1)
        self.uom_unit.write({
            'name': 'Test-Unit',
            'rounding': 1.0})
        self.uom_dozen = self.env['uom.uom'].create({
            'name': 'Test-DozenA',
            'category_id': self.categ_unit.id,
            'factor_inv': 12,
            'uom_type': 'bigger',
            'rounding': 0.001})

        # Create products
        # --------------------------
        route_manufacture = self.warehouse.manufacture_pull_id.route_id
        route_mto = self.warehouse.mto_pull_id.route_id
        product_a = create_product('Product A', self.uom_unit, routes=[route_manufacture, route_mto])
        product_b = create_product('Product B', self.uom_dozen)

        # ------------------------------------------------------------------------------------------
        # Bill of materials for product A, B, D.
        # ------------------------------------------------------------------------------------------

        # Bill of materials for Product A.
        with Form(self.env['mrp.bom']) as f:
            f.product_tmpl_id = product_a.product_tmpl_id
            f.product_qty = 2
            f.product_uom_id = self.uom_dozen
            with f.bom_line_ids.new() as line:
                line.product_id = product_b
                line.product_qty = 3
                line.product_uom_id = self.uom_unit

        # ----------------------------------------
        # Create sales order of 10 Dozen product A.
        # ----------------------------------------

        order_form = Form(self.env['sale.order'])
        order_form.partner_id = self.env.ref('base.res_partner_2')
        with order_form.order_line.new() as line:
            line.product_id = product_a
            line.product_uom = self.uom_dozen
            line.product_uom_qty = 10
        order = order_form.save()
        order.action_confirm()
        self.assertEqual(order.production_count, 1)

        domain = order.action_view_production().get("domain", [])
        self.assertIn(("sale_id", "=", order.id), domain)
