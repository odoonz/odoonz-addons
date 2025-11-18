import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockValuationHistory(models.Model):
    _name = "stock.valuation.historical"
    _description = "Stock Valuation History"
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        readonly=True,
        compute="_compute_name",
        store=True,
        index=True,
    )
    date = fields.Date(
        string="Valuation Date",
        required=True,
        readonly=True,
        default=fields.Date.context_today,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, readonly=True, index=True
    )
    product_categ_id = fields.Many2one(
        "product.category",
        string="Product Category",
        related="product_id.categ_id",
        store=True,
        index=True,
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
        store=True,
    )
    location_id = fields.Many2one(
        "stock.location", string="Location", readonly=True, index=True
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse", readonly=True, index=True
    )
    quantity = fields.Float(readonly=True, digits="Product Unit of Measure")
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        readonly=True,
    )
    value = fields.Monetary(
        string="Total Value", currency_field="currency_id", readonly=True
    )
    cost_price = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_cost_price",
        store=True,
    )
    valuation_account_id = fields.Many2one(
        "account.account", string="Valuation Account", readonly=True, store=True
    )
    cost_method = fields.Selection(
        related="product_categ_id.property_cost_method",
        string="Costing Method",
        readonly=True,
        store=True,
    )

    @api.depends("date")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.date:%d %b %Y}"

    @api.depends("product_id", "quantity", "value")
    def _compute_cost_price(self):
        for record in self:
            if record.quantity:
                record.cost_price = record.value / record.quantity
            else:
                record.cost_price = 0.0

    def _prepare_valuation_lines(self, companies=False):
        """Prepare valuation data from quants.
        :param companies: list of companies to prepare valuation for,
          if False, all companies will be used, maybe necessary
          to have multiple crons if multiple companies in different
          timezones are used
        :return: list of valuation lines
        """
        if not companies:
            companies = self.env["res.company"].sudo().search([])
        vals_list = []
        for company in companies:
            quants = (
                self.env["stock.quant"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("location_id.usage", "=", "internal"),
                    ]
                )
            )
            for quant in quants:
                warehouse = quant.location_id.warehouse_id
                if not warehouse:
                    continue
                product = quant.product_id.with_company(company)
                account = product.categ_id.property_stock_valuation_account_id

                vals_list.append(
                    {
                        "date": fields.Date.context_today(self),
                        "company_id": quant.company_id.id,
                        "product_id": product.id,
                        "location_id": quant.location_id.id,
                        "warehouse_id": warehouse.id,
                        "quantity": quant.quantity,
                        "currency_id": quant.company_id.currency_id.id,
                        "value": quant.value,
                        "valuation_account_id": account.id,
                    }
                )

        return vals_list

    @api.model
    def _create_month_end_valuation(self, companies=False):
        """Create month-end valuation entries."""
        # Delete any existing entries for the same date to avoid duplicates
        company_args = [("company_id", "in", companies.ids)] if companies else []
        existing = self.search(
            [("date", "=", fields.Date.context_today(self))] + company_args
        )
        if existing:
            existing.sudo().unlink()

        vals_list = self._prepare_valuation_lines(companies)
        if not vals_list:
            return False

        return self.sudo().create(vals_list)

    @api.model
    def _run_month_end_valuation(self):
        """Cron job method to create month-end valuation."""
        # Check if last day of month and return if not
        today = fields.Date.context_today(self)
        last_day_of_month = today + relativedelta(day=31)
        if today != last_day_of_month:
            return False
        try:
            self._create_month_end_valuation()
            return True
        except Exception as e:
            # Log error but don't fail the cron job
            _logger.error("Error running month-end stock valuation: %s", str(e))
            return False
