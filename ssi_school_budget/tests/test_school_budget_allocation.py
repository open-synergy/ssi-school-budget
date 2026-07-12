# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo_yaml_test import YamlTransactionCase


@tagged("post_install", "-at_install")
class TestSchoolBudgetAllocation(YamlTransactionCase):
    def test_school_budget_allocation(self):
        self.run_yaml_scenario("test_data_school_budget_allocation.yaml")

    def _setup_budgets(self, suffix):
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "Grade Type Alloc Constrain %s" % suffix,
                "code": "GTALC%s" % suffix,
                "sequence": 10,
            }
        )
        school = self.env["school"].create(
            {
                "name": "School Alloc Constrain %s" % suffix,
                "code": "SCHALC%s" % suffix,
                "grade_type_id": grade_type.id,
            }
        )
        year_1 = self.env["school_academic_year"].create(
            {
                "name": "Year Alloc Constrain %s A" % suffix,
                "code": "AYALC%sA" % suffix,
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        year_2 = self.env["school_academic_year"].create(
            {
                "name": "Year Alloc Constrain %s B" % suffix,
                "code": "AYALC%sB" % suffix,
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        unit_budget = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school.id,
                "academic_year_id": year_1.id,
            }
        )
        center_budget = self.env["school_budget"].create(
            {
                "org_type": "center",
                "academic_year_id": year_1.id,
            }
        )
        center_budget_other_year = self.env["school_budget"].create(
            {
                "org_type": "center",
                "academic_year_id": year_2.id,
            }
        )
        return unit_budget, center_budget, center_budget_other_year

    def test_constrain_contribution_allocation_parent_is_unit_blocks_create(self):
        """A unit budget cannot be the parent of a contribution
        allocation."""
        unit_budget, _center, _center_other = self._setup_budgets("C1")
        with self.assertRaises(ValidationError):
            self.env["school_budget_contribution_allocation"].create(
                {
                    "parent_budget_id": unit_budget.id,
                    "child_budget_id": unit_budget.id,
                }
            )

    def test_constrain_contribution_allocation_different_academic_year_blocks_create(
        self,
    ):
        """Parent and child budgets must share the same academic
        year."""
        unit_budget, _center, center_other_year = self._setup_budgets("C2")
        with self.assertRaises(ValidationError):
            self.env["school_budget_contribution_allocation"].create(
                {
                    "parent_budget_id": center_other_year.id,
                    "child_budget_id": unit_budget.id,
                }
            )

    def test_constrain_parent_expense_allocation_on_unit_blocks_create(self):
        """Parent expense allocations are not allowed on unit
        budgets."""
        unit_budget, _center, _center_other = self._setup_budgets("C3")
        expense_category = self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Alloc Constrain C3",
                "code": "5110.92",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_parent_expense_allocation"].create(
                {
                    "budget_id": unit_budget.id,
                    "expense_category_id": expense_category.id,
                }
            )

    def test_constrain_duplicate_parent_expense_allocation_category_blocks_create(
        self,
    ):
        """Two allocation settings for the same category on the same
        budget must be rejected."""
        _unit_budget, center_budget, _center_other = self._setup_budgets("C4")
        expense_category = self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Alloc Constrain C4",
                "code": "5110.93",
            }
        )
        self.env["school_budget_parent_expense_allocation"].create(
            {
                "budget_id": center_budget.id,
                "expense_category_id": expense_category.id,
            }
        )
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env["school_budget_parent_expense_allocation"].create(
                    {
                        "budget_id": center_budget.id,
                        "expense_category_id": expense_category.id,
                    }
                )
                self.env["school_budget_parent_expense_allocation"].flush()
