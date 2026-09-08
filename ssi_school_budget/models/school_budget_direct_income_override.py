# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetDirectIncomeOverride(models.Model):
    """
    Overrides the automatically computed direct-income amount of a
    single direct-income expense category on a school_budget
    document. The automatic amount is the sum of the foundation
    column of that category's expense lines (BOS is deliberately
    excluded); this record replaces it with a manually entered
    value.
    """

    _name = "school_budget_direct_income_override"
    _description = "School Budget Direct Income Override"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this override belongs to.",
    )
    expense_category_id = fields.Many2one(
        string="Expense Category",
        comodel_name="school_budget_expense_category",
        required=True,
        domain=[("is_direct_income", "=", True)],
        help="The direct-income expense category being overridden.",
    )
    override_amount = fields.Monetary(
        string="Override Amount",
        required=True,
        default=0.0,
        currency_field="currency_id",
        help="Replaces the automatically computed direct-income "
        "amount (sum of the foundation column) for this category.",
    )
    note = fields.Text(
        string="Note",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
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
Context: Save school budget direct income override
Database ID: %s
Problem: Only one direct income override is allowed per expense
category on the same budget
Solution: Edit the existing override instead of creating a
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

    @api.constrains("expense_category_id")
    def _check_direct_income_category(self):
        """Reject an expense category without Direct Income enabled.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_direct_income_category_condition():
                error_message = (
                    _(
                        """
Context: Save school budget direct income override
Database ID: %s
Problem: Expense Category '%s' does not have Direct Income enabled
Solution: Select an expense category with Direct Income enabled
"""
                    )
                    % (
                        record.id,
                        record.expense_category_id.name,
                    )
                )
                raise ValidationError(error_message)

    def _check_direct_income_category_condition(self):
        """Return whether the expense category is direct-income.

        :return: ``True`` when ``expense_category_id.is_direct_income``
        """
        self.ensure_one()
        return self.expense_category_id.is_direct_income

    @api.constrains("override_amount")
    def _check_override_amount(self):
        """Reject a negative override amount.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_override_amount_condition():
                error_message = (
                    _(
                        """
Context: Save school budget direct income override
Database ID: %s
Problem: Override Amount is negative
Solution: Enter zero or a positive number
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_override_amount_condition(self):
        """Return whether ``override_amount`` is non-negative.

        :return: ``True`` when ``override_amount`` >= 0
        """
        self.ensure_one()
        return self.override_amount >= 0
