# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetParentExpenseAllocation(models.Model):
    """
    Marks a single expense category of a branch/center school_budget
    document as pushed down to its children's cost base. When
    affects_up is enabled, the category's amount is split among
    children by new-student proportion (pct_up) and added to their
    UP cost base; otherwise it is split by total-student proportion
    (pct_us) and added to their US cost base. The actual push-down
    math lives in the simulation engine (ssi_school_budget).
    """

    _name = "school_budget_parent_expense_allocation"
    _description = "School Budget Parent Expense Allocation"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The branch/center budget document owning this " "allocation setting.",
    )
    expense_category_id = fields.Many2one(
        string="Expense Category",
        comodel_name="school_budget_expense_category",
        required=True,
        help="The expense category pushed down to children.",
    )
    affects_up = fields.Boolean(
        string="Affects UP",
        default=False,
        help=(
            "When enabled, this cost category is pushed down into "
            "the children's UP base (split by new students). "
            "Otherwise it goes into the US base (split by total "
            "students)."
        ),
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.constrains("budget_id", "expense_category_id")
    def _check_unique_budget_expense_category(self):
        """Reject a duplicate expense category on the same budget.

        Replaces the former ``_sql_constraints`` entry so the
        error is raised as ``ValidationError`` instead of a
        raw ``IntegrityError``.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_unique_budget_expense_category_condition():
                error_message = (
                    _(
                        """
Context: Save school budget parent expense allocation
Database ID: %s
Problem: Only one allocation setting is allowed per expense
category on the same budget
Solution: Edit the existing allocation instead of creating a
duplicate
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_unique_budget_expense_category_condition(self):
        """Return whether the unique key still holds.

        :return: ``True`` when no other record shares the
            same key
        """
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("budget_id", "=", self.budget_id.id),
            ("expense_category_id", "=", self.expense_category_id.id),
        ]
        return self.search_count(domain) == 0

    @api.constrains("budget_id")
    def _check_parent_org_type(self):
        for record in self.sudo():
            if not record._check_parent_org_type_condition():
                error_message = (
                    _(
                        """
Context: Save school budget parent expense allocation
Database ID: %s
Problem: Parent expense allocations are only allowed on branch or
center budgets
Solution: Select a branch/center budget
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_parent_org_type_condition(self):
        self.ensure_one()
        return self.budget_id.org_type in ("branch", "center")
