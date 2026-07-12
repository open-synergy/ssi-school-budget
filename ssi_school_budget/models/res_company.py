# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    """
    Extends res.company (the Center in the school organization
    hierarchy) with the Analytic Account used to pull the center's
    own budget realization from posted journal items
    (ssi_school_budget). The account is deliberately a plain field
    here (not compute) since a company does not have a parent
    organization to derive it from.
    """

    _name = "res.company"
    _inherit = ["res.company"]

    school_analytic_account_id = fields.Many2one(
        string="School Budget Analytic Account",
        comodel_name="account.analytic.account",
        help="Analytic Account representing this Center on School "
        "Budget realization. Must not be shared with any branch or "
        "school unit.",
    )
    school_analytic_group_id = fields.Many2one(
        string="School Budget Analytic Group",
        comodel_name="account.analytic.group",
        help="Root Analytic Group under which branch/unit analytic "
        "groups are nested, for roll-up reporting.",
    )

    @api.constrains("school_analytic_account_id")
    def _check_school_analytic_account_unique(self):
        for record in self.sudo():
            if not record._check_school_analytic_account_unique_condition():
                error_message = (
                    _(
                        """
Context: Save company
Database ID: %s
Problem: Analytic Account '%s' is already used by another company,
branch, or school unit for School Budget realization
Solution: Select an Analytic Account that is not used elsewhere
"""
                    )
                    % (
                        record.id,
                        record.school_analytic_account_id.display_name,
                    )
                )
                raise ValidationError(error_message)

    def _check_school_analytic_account_unique_condition(self):
        self.ensure_one()
        if not self.school_analytic_account_id:
            return True
        aa_id = self.school_analytic_account_id.id
        if self.search_count(
            [("school_analytic_account_id", "=", aa_id), ("id", "!=", self.id)]
        ):
            return False
        if self.env["school_branch"].search_count(
            [("analytic_account_id", "=", aa_id)]
        ):
            return False
        if self.env["school"].search_count([("analytic_account_id", "=", aa_id)]):
            return False
        return True
