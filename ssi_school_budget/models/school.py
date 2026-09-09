# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class School(models.Model):
    """
    Extends school with the Analytic Account used to pull this
    unit's own budget realization from posted journal items
    (ssi_school_budget).
    """

    _name = "school"
    _inherit = ["school"]

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        help="Analytic Account representing this school unit on "
        "School Budget realization. Must not be shared with the "
        "company or any branch.",
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

        The new account is nested under the branch's analytic group
        when this school belongs to a branch, otherwise under the
        company's ``school_analytic_group_id``.
        """
        self.ensure_one()
        if self.analytic_account_id:
            return
        group_id = (
            self.branch_id.analytic_group_id.id
            if self.branch_id
            else self.company_id.school_analytic_group_id.id
        )
        self.analytic_account_id = self.env["account.analytic.account"].create(
            {
                "name": self.name,
                "code": self.code,
                "group_id": group_id,
                "company_id": self.company_id.id,
            }
        )

    @api.constrains("analytic_account_id")
    def _check_school_analytic_account_unique(self):
        """Reject an analytic account already used elsewhere.

        Checks against other schools, branches, and companies.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_school_analytic_account_unique_condition():
                error_message = (
                    _(
                        """
Context: Save school
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

        :return: ``True`` when no other school, branch, or company
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
        if self.env["school_branch"].search_count(
            [("analytic_account_id", "=", aa_id)]
        ):
            return False
        if self.env["res.company"].search_count(
            [("school_analytic_account_id", "=", aa_id)]
        ):
            return False
        return True
