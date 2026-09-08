# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudgetSubsidy(YamlTransactionCase):
    """YAML scenario and Python constraint tests for subsidies."""

    def test_school_budget_subsidy(self):
        """Run the school_budget_subsidy YAML scenario."""
        self.run_yaml_scenario("test_data_school_budget_subsidy.yaml")

    def _setup_two_branches(self, suffix):
        """Create two branches, each with a unit, plus a center budget.

        :param suffix: unique suffix appended to fixture names/codes
        :return: dict with keys ``budget_center``, ``budget_branch_a``,
            ``budget_unit_a``, ``budget_unit_b``, ``expense_category``,
            and ``income_category``
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "Grade Type Subsidy Constrain %s" % suffix,
                "code": "GTSC%s" % suffix,
                "sequence": 10,
            }
        )
        branch_a = self.env["school_branch"].create(
            {
                "name": "Branch Subsidy Constrain A %s" % suffix,
                "code": "BRSCA%s" % suffix,
            }
        )
        branch_b = self.env["school_branch"].create(
            {
                "name": "Branch Subsidy Constrain B %s" % suffix,
                "code": "BRSCB%s" % suffix,
            }
        )
        school_a = self.env["school"].create(
            {
                "name": "School Subsidy Constrain A %s" % suffix,
                "code": "SCHSCA%s" % suffix,
                "grade_type_id": grade_type.id,
                "branch_id": branch_a.id,
            }
        )
        school_b = self.env["school"].create(
            {
                "name": "School Subsidy Constrain B %s" % suffix,
                "code": "SCHSCB%s" % suffix,
                "grade_type_id": grade_type.id,
                "branch_id": branch_b.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "Year Subsidy Constrain %s" % suffix,
                "code": "AYSC%s" % suffix,
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        budget_center = self.env["school_budget"].create(
            {"org_type": "center", "academic_year_id": academic_year.id}
        )
        budget_branch_a = self.env["school_budget"].create(
            {
                "org_type": "branch",
                "branch_id": branch_a.id,
                "academic_year_id": academic_year.id,
            }
        )
        budget_unit_a = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school_a.id,
                "academic_year_id": academic_year.id,
            }
        )
        budget_unit_b = self.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": school_b.id,
                "academic_year_id": academic_year.id,
            }
        )
        expense_category = self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Subsidy Constrain %s" % suffix,
                "code": "5110.7%s" % suffix,
            }
        )
        income_category = self.env["school_budget_income_category"].create(
            {
                "name": "Income Subsidy Constrain %s" % suffix,
                "code": "4120.7%s" % suffix,
                "calc_method": "manual",
            }
        )
        return {
            "budget_center": budget_center,
            "budget_branch_a": budget_branch_a,
            "budget_unit_a": budget_unit_a,
            "budget_unit_b": budget_unit_b,
            "expense_category": expense_category,
            "income_category": income_category,
        }

    def test_constrain_branch_subsidy_to_other_branch_unit_blocks_create(self):
        """A branch cannot subsidize a unit that is not its own
        child."""
        data = self._setup_two_branches("1")
        with self.assertRaises(ValidationError):
            self.env["school_budget_subsidy"].create(
                {
                    "provider_budget_id": data["budget_branch_a"].id,
                    "recipient_budget_id": data["budget_unit_b"].id,
                    "expense_category_id": data["expense_category"].id,
                    "income_category_id": data["income_category"].id,
                    "amount": 1000000,
                }
            )

    def test_constrain_unit_subsidy_provider_blocks_create(self):
        """A unit budget cannot be a subsidy provider."""
        data = self._setup_two_branches("2")
        with self.assertRaises(ValidationError):
            self.env["school_budget_subsidy"].create(
                {
                    "provider_budget_id": data["budget_unit_a"].id,
                    "recipient_budget_id": data["budget_unit_b"].id,
                    "expense_category_id": data["expense_category"].id,
                    "income_category_id": data["income_category"].id,
                    "amount": 1000000,
                }
            )

    def test_constrain_subsidy_to_center_blocks_create(self):
        """A subsidy recipient cannot be a center budget."""
        data = self._setup_two_branches("3")
        with self.assertRaises(ValidationError):
            self.env["school_budget_subsidy"].create(
                {
                    "provider_budget_id": data["budget_center"].id,
                    "recipient_budget_id": data["budget_center"].id,
                    "expense_category_id": data["expense_category"].id,
                    "income_category_id": data["income_category"].id,
                    "amount": 1000000,
                }
            )

    def test_constrain_direct_income_override_on_non_direct_income_category(self):
        """A direct income override on a non-direct-income category
        must be rejected."""
        data = self._setup_two_branches("4")
        with self.assertRaises(ValidationError):
            self.env["school_budget_direct_income_override"].create(
                {
                    "budget_id": data["budget_unit_a"].id,
                    "expense_category_id": data["expense_category"].id,
                    "override_amount": 1000000,
                }
            )

    def test_constrain_negative_direct_income_override_amount_blocks_create(self):
        """override_amount must not be negative."""
        data = self._setup_two_branches("5")
        target_income_category = self.env["school_budget_income_category"].create(
            {
                "name": "Direct Income Target Constrain 5",
                "code": "4120.85",
                "calc_method": "from_expense",
            }
        )
        direct_income_expense_category = self.env[
            "school_budget_expense_category"
        ].create(
            {
                "name": "Direct Income Expense Constrain 5",
                "code": "5140.75",
                "is_direct_income": True,
                "maps_to_income_category_id": target_income_category.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_direct_income_override"].create(
                {
                    "budget_id": data["budget_unit_a"].id,
                    "expense_category_id": direct_income_expense_category.id,
                    "override_amount": -1,
                }
            )

    def test_constrain_duplicate_direct_income_override_category_blocks_create(self):
        """Two overrides for the same category on the same budget
        must be rejected."""
        data = self._setup_two_branches("6")
        target_income_category = self.env["school_budget_income_category"].create(
            {
                "name": "Direct Income Target Constrain 6",
                "code": "4120.86",
                "calc_method": "from_expense",
            }
        )
        direct_income_expense_category = self.env[
            "school_budget_expense_category"
        ].create(
            {
                "name": "Direct Income Expense Constrain 6",
                "code": "5140.76",
                "is_direct_income": True,
                "maps_to_income_category_id": target_income_category.id,
            }
        )
        self.env["school_budget_direct_income_override"].create(
            {
                "budget_id": data["budget_unit_a"].id,
                "expense_category_id": direct_income_expense_category.id,
                "override_amount": 1000000,
            }
        )
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env["school_budget_direct_income_override"].create(
                    {
                        "budget_id": data["budget_unit_a"].id,
                        "expense_category_id": direct_income_expense_category.id,
                        "override_amount": 2000000,
                    }
                )
                self.env["school_budget_direct_income_override"].flush()
