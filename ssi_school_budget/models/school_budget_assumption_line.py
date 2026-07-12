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

    _sql_constraints = [
        (
            "unique_budget_grade",
            "unique(budget_id, grade_id)",
            "Only one assumption line is allowed per grade on the " "same budget.",
        ),
    ]

    @api.constrains("student_count")
    def _check_student_count(self):
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
        self.ensure_one()
        return self.student_count >= 0
