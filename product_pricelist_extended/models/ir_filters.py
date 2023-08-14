# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv import expression

# To extend you will need to import this list and append.
MODEL_NAMES = [
    "product.product",
    "product.template",
    "product.category",
]


class IrFilters(models.Model):
    _name = "ir.filters"
    _inherit = ["ir.filters", "mail.thread", "mail.activity.mixin"]

    description = fields.Text()

    @api.model
    def _get_default_is_assortment(self):
        if self.env.context.get("product_assortment", False):
            return True
        return False

    # NOTE: If extending with other models, make sure your whitelist/blacklist
    # fields are named in the same way, last word of the model in whitelist_<last>_ids
    # and blacklist_<last>_ids
    blacklist_product_ids = fields.Many2many(
        comodel_name="product.product", relation="assortment_product_blacklisted"
    )
    whitelist_product_ids = fields.Many2many(
        comodel_name="product.product", relation="assortment_product_whitelisted"
    )
    blacklist_template_ids = fields.Many2many(
        comodel_name="product.template", relation="assortment_tmpl_blacklisted"
    )
    whitelist_template_ids = fields.Many2many(
        comodel_name="product.template", relation="assortment_tmpl_whitelisted"
    )
    blacklist_category_ids = fields.Many2many(
        comodel_name="product.category", relation="assortment_categ_blacklisted"
    )
    whitelist_category_ids = fields.Many2many(
        comodel_name="product.category", relation="assortment_categ_whitelisted"
    )
    record_count = fields.Integer(compute="_compute_record_count")
    tmpl_record_count = fields.Integer(compute="_compute_record_count")
    categ_record_count = fields.Integer(compute="_compute_record_count")
    pricelist_record_count = fields.Integer(compute="_compute_record_count")
    is_assortment = fields.Boolean(default=lambda x: x._get_default_is_assortment())
    show_in_filters = fields.Boolean(default=False)

    @api.model
    def _list_all_models(self):
        if self.is_assortment or self.env.context.get("product_assortment", False):
            self._cr.execute(
                "SELECT model, name FROM ir_model WHERE model IN %s ORDER BY name",
                [tuple(MODEL_NAMES)],
            )
            return self._cr.fetchall()
        return super()._list_all_models()

    def _get_eval_domain(self):
        res = super()._get_eval_domain()
        if not self.is_assortment:
            return res
        if self[f"whitelist_{self.model_id.split('.')[-1]}_ids"]:
            result_domain = [
                ("id", "in", self[f"whitelist_{self.model_id.split('.')[-1]}_ids"].ids)
            ]
            res = expression.OR([result_domain, res])
        if self[f"blacklist_{self.model_id.split('.')[-1]}_ids"]:
            result_domain = [
                (
                    "id",
                    "not in",
                    self[f"blacklist_{self.model_id.split('.')[-1]}_ids"].ids,
                )
            ]
            res = expression.AND([result_domain, res])
        return res

    @api.onchange("model_id")
    def _onchange_model_id(self):
        """Onchange to clear irrelevant inclusions and exclusions. Deliberately a
        bit longwinded in order to allow model extensions for things such as supplierinfo where
        we might want to include or exclude quite differently."""
        if self.model_id == "product.product":
            self.whitelist_template_ids = False
            self.blacklist_template_ids = False
            self.whitelist_category_ids = False
            self.blacklist_category_ids = False
        elif self.model_id == "product.template":
            self.whitelist_template_ids = self.whitelist_product_ids.product_tmpl_id
            self.blacklist_template_ids = self.blacklist_product_ids.product_tmpl_id
            self.whitelist_product_ids = False
            self.blacklist_product_ids = False
            self.whitelist_category_ids = False
            self.blacklist_category_ids = False
        elif self.model_id == "product.category":
            self.whitelist_product_ids = False
            self.blacklist_product_ids = False
            self.whitelist_template_ids = False
            self.blacklist_template_ids = False

    def _get_eval_domain_product(self):
        orig_res = self._get_eval_domain()
        new_res = []
        if self.model_id == "product.template":
            for arg in orig_res:
                if len(arg) == 3:
                    if arg[0] == "id":
                        new_res.append(("product_tmpl_id", arg[1], arg[2]))
                    else:
                        new_res.append((f"product_tmpl_id.{arg[0]}", arg[1], arg[2]))
                else:
                    new_res.append(arg)
        elif self.model_id == "product.category":
            for arg in orig_res:
                if len(arg) == 3:
                    if arg[0] == "id":
                        new_res.append(("categ_id", arg[1], arg[2]))
                    else:
                        new_res.append((f"categ_id.{arg[0]}", arg[1], arg[2]))
                else:
                    new_res.append(arg)
        else:
            return orig_res
        return new_res

    def _get_eval_domain_template(self):
        orig_res = self._get_eval_domain()
        new_res = []
        if self.model_id == "product.category":
            for arg in orig_res:
                if len(arg) == 3:
                    if arg[0] == "id":
                        new_res.append(("categ_id", arg[1], arg[2]))
                    else:
                        new_res.append((f"categ_id.{arg[0]}", arg[1], arg[2]))
                else:
                    new_res.append(arg)
        elif self.model_id == "product.product":
            return [
                (
                    "id",
                    "in",
                    self.env["product.product"].search(orig_res).product_tmpl_id.ids,
                )
            ]
        else:
            return orig_res
        return new_res

    def _get_pricelist_domain(self):
        self.ensure_one()
        return [
            (
                "id",
                "in",
                self.env["product.pricelist.assortment.item"]
                .search([("assortment_filter_id", "=", self.id)])
                .pricelist_id.ids,
            )
        ]

    def _compute_record_count(self):
        for record in self:
            if record.model_id not in self.env:
                # invalid model
                record.record_count = 0
                record.tmpl_record_count = 0
                record.categ_record_count = 0
                record.pricelist_record_count = 0
                continue
            domain = record._get_pricelist_domain()
            record.pricelist_record_count = self.env["product.pricelist"].search_count(
                domain
            )
            domain = record._get_eval_domain_product()
            record.record_count = self.env["product.product"].search_count(domain)
            if record.model_id == "product.product":
                record.tmpl_record_count = 0
                record.categ_record_count = 0
                continue
            domain = record._get_eval_domain_template()
            record.tmpl_record_count = self.env["product.template"].search_count(domain)
            if record.model_id == "product.template":
                record.categ_record_count = 0
                continue
            domain = record._get_eval_domain()
            record.categ_record_count = self.env["product.category"].search_count(
                domain
            )

    @api.model
    def _get_action_domain(self, action_id=None):
        # tricky way to act on get_filter method to prevent returning
        # assortment in search view filters
        domain = super()._get_action_domain(action_id=action_id)
        domain = expression.AND(
            [
                ["|", ("is_assortment", "=", False), ("show_in_filters", "=", True)],
                domain,
            ]
        )
        return domain

    def show_products(self):
        self.ensure_one()
        xmlid = "product.product_normal_action_sell"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "domain": self._get_eval_domain_product(),
                "name": _("Products"),
                "context": self.env.context,
                "target": "current",
            }
        )
        return action

    def show_templates(self):
        self.ensure_one()
        xmlid = "product.product_template_action_all"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "domain": self._get_eval_domain_template(),
                "name": _("Products"),
                "context": self.env.context,
                "target": "current",
            }
        )
        return action

    def show_categories(self):
        self.ensure_one()
        xmlid = "product.product_category_action_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "domain": self._get_eval_domain(),
                "name": _("Categories"),
                "context": self.env.context,
                "target": "current",
            }
        )
        return action

    def show_pricelists(self):
        self.ensure_one()
        xmlid = "product.product_pricelist_action2"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "domain": self._get_pricelist_domain(),
                "name": _("Pricelists"),
                "context": self.env.context,
                "target": "current",
            }
        )
        return action
