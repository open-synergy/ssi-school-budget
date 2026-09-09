# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBranch(models.Model):
    """
    Extends school_branch with the Analytic Account used to pull
    this branch's own budget realization from posted journal items
    (ssi_school_budget), plus an Analytic Group used to nest its
    school units' analytic accounts for roll-up reporting.
    """

    _name = "school_branch"
    _inherit = ["school_branch"]

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        help="Analytic Account representing this branch on School "
        "Budget realization. Must not be shared with the company or "
        "any school unit.",
    )
    analytic_group_id = fields.Many2one(
        string="Analytic Group",
        comodel_name="account.analytic.group",
        help="Analytic Group under which this branch's school units' "
        "analytic accounts are nested, for roll-up reporting.",
    )

    def action_create_analytic_account(self):
        """Create the School Budget analytic account for each record.

        Button action layer; delegates to
        ``_create_analytic_account()`` per record.
        """
        for record in self.sudo():
            record._create_analytic_account()

    def _create_analytic_account(self):
        """Create and assign ``analytic_account_id`` if not set yet.

        The new account is nested under this branch's own
        ``analytic_group_id``.
        """
        self.ensure_one()
        if self.analytic_account_id:
            return
        self.analytic_account_id = self.env["account.analytic.account"].create(
            {
                "name": self.name,
                "code": self.code,
                "group_id": self.analytic_group_id.id,
                "company_id": self.company_id.id,
            }
        )

    @api.constrains("analytic_account_id")
    def _check_school_analytic_account_unique(self):
        """Reject an analytic account already used elsewhere.

        Checks against other branches, schools, and companies.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_school_analytic_account_unique_condition():
                error_message = (
                    _(
                        """
Context: Save school branch
Database ID: %s
Problem: Analytic Account '%s' is already used by another company,
branch, or school unit for School Budget realization
Solution: Select an Analytic Account that is not used elsewhere
"""
                    )
                    % (
                        record.id,
                        record.analytic_account_id.display_name,
                    )
                )
                raise ValidationError(error_message)

    def _check_school_analytic_account_unique_condition(self):
        """Return whether ``analytic_account_id`` is unique.

        :return: ``True`` when no other branch, school, or company
            uses the same analytic account
        """
        self.ensure_one()
        if not self.analytic_account_id:
            return True
        aa_id = self.analytic_account_id.id
        if self.search_count(
            [("analytic_account_id", "=", aa_id), ("id", "!=", self.id)]
        ):
            return False
        if self.env["school"].search_count([("analytic_account_id", "=", aa_id)]):
            return False
        if self.env["res.company"].search_count(
            [("school_analytic_account_id", "=", aa_id)]
        ):
            return False
        return True
