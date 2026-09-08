# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudgetExpenseIncomeLine(YamlTransactionCase):
    """YAML scenario and Python constraint tests for expense/income lines."""

    def test_school_budget_expense_income_line(self):
        """Run the school_budget_expense_income_line YAML scenario."""
        self.run_yaml_scenario("test_data_school_budget_expense_income_line.yaml")

    def _setup_budget(self, suffix):
        """Create a grade type, school, academic year, and budget fixture.

        :param suffix: unique suffix appended to fixture names/codes
        :return: tuple ``(grade_type, school, budget)``
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "Grade Type Line Constrain %s" % suffix,
                "code": "GTLC%s" % suffix,
                "sequence": 10,
            }
        )
        school = self.env["school"].create(
            {
                "name": "School Line Constrain %s" % suffix,
                "code": "SCHLC%s" % suffix,
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "Year Line Constrain %s" % suffix,
                "code": "AYLC%s" % suffix,
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        budget = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school.id,
                "academic_year_id": academic_year.id,
            }
        )
        return grade_type, school, budget

    def test_constrain_income_line_non_manual_category_blocks_create(self):
        """Income lines can only be created under manual-calc-method
        income categories.

        Pure Python -- trigger P10 (L-09/L-10: the fixture builds a
        grade type, school, academic year, and budget
        programmatically across several linked models, which the
        ``EVAL:`` sandbox cannot express).
        """
        _grade_type, _school, budget = self._setup_budget("I1")
        income_category = self.env["school_budget_income_category"].create(
            {
                "name": "Simulated UP Constrain I1",
                "code": "4110.90",
                "calc_method": "simulated_up",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_income_line"].create(
                {
                    "budget_id": budget.id,
                    "income_category_id": income_category.id,
                    "amount": 1000000,
                }
            )

    def test_constrain_expense_line_number_zero_blocks_create(self):
        """line_number=0 on an expense line must be rejected.

        Pure Python -- trigger P10 (L-09/L-10: the fixture builds a
        grade type, school, academic year, and budget
        programmatically across several linked models, which the
        ``EVAL:`` sandbox cannot express).
        """
        _grade_type, _school, budget = self._setup_budget("E1")
        expense_category = self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Constrain E1",
                "code": "5110.90",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_expense_line"].create(
                {
                    "budget_id": budget.id,
                    "expense_category_id": expense_category.id,
                    "line_number": 0,
                    "foundation": 1000000,
                }
            )

    def test_constrain_duplicate_grade_allocation_same_grade_blocks_create(self):
        """Two grade allocations for the same grade on the same
        expense line must be rejected.

        Pure Python — trigger P10 (L-09/L-10: the fixture builds a
        grade type, school, academic year, budget, expense line, and
        grade programmatically across several linked models, which
        the ``EVAL:`` sandbox cannot express).
        """
        grade_type, _school, budget = self._setup_budget("G1")
        expense_category = self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Constrain G1",
                "code": "5110.91",
            }
        )
        grade = self.env["school_grade"].create(
            {
                "name": "Grade Constrain G1",
                "code": "GCG1",
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        expense_line = self.env["school_budget_expense_line"].create(
            {
                "budget_id": budget.id,
                "expense_category_id": expense_category.id,
                "foundation": 1000000,
            }
        )
        self.env["school_budget_expense_grade_allocation"].create(
            {
                "line_id": expense_line.id,
                "grade_id": grade.id,
                "amount": 500000,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_expense_grade_allocation"].create(
                {
                    "line_id": expense_line.id,
                    "grade_id": grade.id,
                    "amount": 200000,
                }
            )
