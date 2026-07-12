# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudgetAnalyticAccount(YamlTransactionCase):
    def test_school_budget_analytic_account(self):
        self.run_yaml_scenario("test_data_school_budget_analytic_account.yaml")

    def test_constrain_analytic_account_reused_by_other_unit_blocks_write(self):
        """Assigning an analytic account already used by another
        school unit must be rejected."""
        grade_type = self.env["school_grade_type"].create(
            {"name": "Grade Type AA Constrain 1", "code": "GTAAC1", "sequence": 10}
        )
        school_a = self.env["school"].create(
            {
                "name": "School AA Constrain 1A",
                "code": "SCHAAC1A",
                "grade_type_id": grade_type.id,
            }
        )
        school_b = self.env["school"].create(
            {
                "name": "School AA Constrain 1B",
                "code": "SCHAAC1B",
                "grade_type_id": grade_type.id,
            }
        )
        school_a.action_create_analytic_account()
        with self.assertRaises(ValidationError):
            school_b.write({"analytic_account_id": school_a.analytic_account_id.id})

    def test_constrain_analytic_account_reused_by_branch_blocks_write(self):
        """Assigning a unit's analytic account to a branch must be
        rejected."""
        grade_type = self.env["school_grade_type"].create(
            {"name": "Grade Type AA Constrain 2", "code": "GTAAC2", "sequence": 10}
        )
        school = self.env["school"].create(
            {
                "name": "School AA Constrain 2",
                "code": "SCHAAC2",
                "grade_type_id": grade_type.id,
            }
        )
        branch = self.env["school_branch"].create(
            {"name": "Branch AA Constrain 2", "code": "BRAAC2"}
        )
        school.action_create_analytic_account()
        with self.assertRaises(ValidationError):
            branch.write({"analytic_account_id": school.analytic_account_id.id})

    def test_constrain_confirm_budget_without_analytic_account_blocks(self):
        """Confirming a budget whose organization has no analytic
        account must raise a UserError."""
        grade_type = self.env["school_grade_type"].create(
            {"name": "Grade Type AA Constrain 3", "code": "GTAAC3", "sequence": 10}
        )
        school = self.env["school"].create(
            {
                "name": "School AA Constrain 3",
                "code": "SCHAAC3",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "Year AA Constrain 3",
                "code": "AYAAC3",
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
        with self.assertRaises(UserError):
            budget.action_confirm()
