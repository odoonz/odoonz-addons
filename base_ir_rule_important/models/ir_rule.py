# Copyright 2024 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):

    _inherit = "ir.rule"

    important = fields.Boolean(default=False, copy=False)

    @api.constrains("important", "groups")
    def _check_important(self):
        for record in self:
            if record.important and not record.groups:
                record.important = False

    def _get_important_rules(self, model_name, mode="read"):
        """Returns all the rules matching the model for the mode for the
        current user.
        """
        if mode not in self._MODES:
            raise ValueError("Invalid mode: %r" % (mode,))

        if self.env.su:
            return self.browse(())

        query = """ SELECT r.id FROM ir_rule r JOIN ir_model m ON (r.model_id=m.id)
                    WHERE m.model=%s AND r.active AND r.important AND r.perm_{mode}
                    AND r.id IN (SELECT rule_group_id FROM rule_group_rel rg
                                  JOIN res_groups_users_rel gu ON (rg.group_id=gu.gid)
                                  WHERE gu.uid=%s)
                    ORDER BY r.id
                """.format(
            mode=mode
        )
        self._cr.execute(query, (model_name, self._uid))
        return self.browse(row[0] for row in self._cr.fetchall())

    def _get_rules(self, model_name, mode="read"):
        # This is dumb and probably more expensive than just letting them go
        return self.browse(
            super()
            ._get_rules(model_name, mode=mode)
            .sudo()
            .filtered(lambda s: not s.important)
            .ids
        )

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        domain = super()._compute_domain(model_name, mode=mode)
        rules = self._get_important_rules(model_name, mode=mode)
        if not rules:
            return domain

        # browse user and rules as SUPERUSER_ID to avoid access errors!
        eval_context = self._eval_context()
        user_groups = self.env.user.groups_id
        important_domains = []
        for rule in rules.sudo():
            # evaluate the domain for the current user
            dom = (
                safe_eval(rule.domain_force, eval_context) if rule.domain_force else []
            )
            dom = expression.normalize_domain(dom)
            if rule.groups & user_groups:
                important_domains.append(dom)

        # combine domains
        if not important_domains:
            return domain
        return expression.AND(important_domains + [domain])
