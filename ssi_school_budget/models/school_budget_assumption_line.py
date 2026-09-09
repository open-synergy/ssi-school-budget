# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetAssumptionLine(models.Model):
    """
    Represents the planned student headcount of a single grade
    within a school_budget document (org_type=unit only). The sum
    of student_count across all lines feeds total_student_count,
    which is later used as the divisor of the US tariff simulation
    (ssi_school_budget).
    """

    _name = "school_budget_assumption_line"
    _description = "School Budget Student Assumption"
    _order = "grade_id, id"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this assumption line belongs to.",
    )
    grade_id = fields.Many2one(
        string="Grade",
        comodel_name="school_grade",
        required=True,
        help="The grade level this student count applies to.",
    )
    student_count = fields.Integer(
        string="Student Count",
        default=0,
        help="Number of students planned for this grade.",
    )

    @api.constrains("budget_id", "grade_id")
    def _check_unique_budget_grade(self):
        """Reject a duplicate grade on the same budget.

        Replaces the former ``_sql_constraints`` entry so the error
        is raised as ``ValidationError`` instead of a raw
        ``IntegrityError``.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_unique_budget_grade_condition():
                error_message = (
                    _(
                        """
Context: Save school budget assumption line
Database ID: %s
Problem: Only one assumption line is allowed per grade on the
same budget
Solution: Edit the existing line instead of creating a duplicate
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_unique_budget_grade_condition(self):
        """Return whether ``grade_id`` is unique on this budget.

        :return: ``True`` when no other line shares the same
            ``budget_id``/``grade_id`` pair
        """
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("budget_id", "=", self.budget_id.id),
            ("grade_id", "=", self.grade_id.id),
        ]
        return self.search_count(domain) == 0

    @api.constrains("student_count")
    def _check_student_count(self):
        """Reject a negative student count.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_student_count_condition():
                error_message = (
                    _(
                        """
Context: Save school budget assumption line
Database ID: %s
Problem: Student Count is negative
Solution: Enter zero or a positive number
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_student_count_condition(self):
        """Return whether ``student_count`` is non-negative.

        :return: ``True`` when ``student_count`` >= 0
        """
        self.ensure_one()
        return self.student_count >= 0

    @api.constrains("budget_id")
    def _check_budget_org_type(self):
        """Reject a line whose budget is not org_type=unit.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_budget_org_type_condition():
                error_message = (
                    _(
                        """
Context: Save school budget assumption line
Database ID: %s
Problem: Student assumption lines are only allowed when the
budget's Organization Type is Unit
Solution: Remove this line, or change the budget's Organization
Type to Unit
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_budget_org_type_condition(self):
        """Return whether the parent budget is org_type=unit.

        :return: ``True`` when ``budget_id.org_type == "unit"``
        """
        self.ensure_one()
        return self.budget_id.org_type == "unit"
