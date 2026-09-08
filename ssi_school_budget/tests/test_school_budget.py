# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudget(YamlTransactionCase):
    """YAML scenario and Python constraint tests for school_budget."""

    def test_school_budget(self):
        """Run the school_budget YAML scenario."""
        self.run_yaml_scenario("test_data_school_budget.yaml")

    def _setup_school(self, suffix):
        """Create a grade type, school, and academic year fixture.

        :param suffix: unique suffix appended to fixture names/codes
        :return: tuple ``(school, academic_year)``
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "Grade Type Budget Constrain %s" % suffix,
                "code": "GTBC%s" % suffix,
                "sequence": 10,
            }
        )
        school = self.env["school"].create(
            {
                "name": "School Budget Constrain %s" % suffix,
                "code": "SCHBC%s" % suffix,
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "Year Budget Constrain %s" % suffix,
                "code": "AYBC%s" % suffix,
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        return school, academic_year

    def test_constrain_unit_without_school_blocks_create(self):
        """org_type=unit without school_id must be rejected."""
        _school, academic_year = self._setup_school("U1")
        with self.assertRaises(ValidationError):
            self.env["school_budget"].create(
                {
                    "org_type": "unit",
                    "academic_year_id": academic_year.id,
                }
            )

    def test_constrain_center_with_school_blocks_create(self):
        """org_type=center with school_id set must be rejected."""
        school, academic_year = self._setup_school("C1")
        with self.assertRaises(ValidationError):
            self.env["school_budget"].create(
                {
                    "org_type": "center",
                    "school_id": school.id,
                    "academic_year_id": academic_year.id,
                }
            )

    def test_constrain_duplicate_budget_same_org_and_year_blocks_create(self):
        """A second budget for the same organization and academic
        year must be rejected."""
        school, academic_year = self._setup_school("D1")
        self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school.id,
                "academic_year_id": academic_year.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget"].create(
                {
                    "org_type": "unit",
                    "school_id": school.id,
                    "academic_year_id": academic_year.id,
                }
            )

    def _create_grade(self, grade_type, suffix):
        """Create a school_grade fixture under ``grade_type``.

        :param grade_type: the ``school_grade_type`` record
        :param suffix: unique suffix appended to fixture names/codes
        :return: the created ``school_grade`` record
        """
        return self.env["school_grade"].create(
            {
                "name": "Grade Assumption %s" % suffix,
                "code": "GA%s" % suffix,
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )

    def test_constrain_duplicate_assumption_line_same_grade_blocks_create(self):
        """Two assumption lines for the same grade on the same
        budget must be rejected."""
        school, academic_year = self._setup_school("A1")
        grade = self._create_grade(school.grade_type_id, "A1")
        budget = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school.id,
                "academic_year_id": academic_year.id,
            }
        )
        self.env["school_budget_assumption_line"].create(
            {
                "budget_id": budget.id,
                "grade_id": grade.id,
                "student_count": 10,
            }
        )
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env["school_budget_assumption_line"].create(
                    {
                        "budget_id": budget.id,
                        "grade_id": grade.id,
                        "student_count": 5,
                    }
                )
                self.env["school_budget_assumption_line"].flush()

    def test_constrain_assumption_line_on_non_unit_budget_blocks_create(self):
        """Assumption lines are not allowed on branch/center
        budgets."""
        school, academic_year = self._setup_school("A2")
        grade = self._create_grade(school.grade_type_id, "A2")
        budget = self.env["school_budget"].create(
            {
                "org_type": "center",
                "academic_year_id": academic_year.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_assumption_line"].create(
                {
                    "budget_id": budget.id,
                    "grade_id": grade.id,
                    "student_count": 10,
                }
            )

    def test_constrain_negative_student_count_blocks_create(self):
        """A negative student_count on an assumption line must be
        rejected."""
        school, academic_year = self._setup_school("A3")
        grade = self._create_grade(school.grade_type_id, "A3")
        budget = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school.id,
                "academic_year_id": academic_year.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_assumption_line"].create(
                {
                    "budget_id": budget.id,
                    "grade_id": grade.id,
                    "student_count": -1,
                }
            )
