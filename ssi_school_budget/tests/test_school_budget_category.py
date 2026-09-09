# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudgetCategory(YamlTransactionCase):
    """YAML scenario and Python constraint tests for categories."""

    def test_school_budget_category(self):
        """Run the school_budget_category YAML scenario."""
        self.run_yaml_scenario("test_data_school_budget_category.yaml")

    def test_constrain_direct_income_without_target_blocks_create(self):
        """A direct-income expense category without a target income
        category must be rejected.

        Pure Python -- trigger P10 (L-09: kept alongside its sibling
        Python constraint tests in this class rather than split into
        a separate YAML scenario for a single negative-path check).
        """
        with self.assertRaises(ValidationError):
            self.env["school_budget_expense_category"].create(
                {
                    "name": "Direct Income Bad",
                    "code": "5140.01",
                    "is_direct_income": True,
                }
            )

    def test_constrain_investment_category_zero_economic_life_blocks_create(self):
        """An investment category with default_economic_life <= 0
        must be rejected.

        Pure Python -- trigger P10 (L-09: kept alongside its sibling
        Python constraint tests in this class rather than split into
        a separate YAML scenario for a single negative-path check).
        """
        with self.assertRaises(ValidationError):
            self.env["school_budget_investment_category"].create(
                {
                    "name": "Bad Investment",
                    "code": "1330.02",
                    "default_economic_life": 0,
                }
            )

    def test_constrain_duplicate_account_same_model_blocks_create(self):
        """Two expense categories cannot map to the same account.

        Pure Python -- trigger P10 (L-09/L-10: the fixture creates
        an ``account.account`` record via ``env.ref`` for the
        account type, which the ``EVAL:`` sandbox cannot express).
        """
        account_type = self.env.ref("account.data_account_type_expenses")
        account = self.env["account.account"].create(
            {
                "name": "Account Constrain 1",
                "code": "5199.90",
                "user_type_id": account_type.id,
            }
        )
        self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Constrain Account 1",
                "code": "5160.90",
                "account_id": account.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_expense_category"].create(
                {
                    "name": "Expense Constrain Account 2",
                    "code": "5160.91",
                    "account_id": account.id,
                }
            )

    def test_constrain_duplicate_account_cross_model_blocks_create(self):
        """An expense category and an income category cannot map to
        the same account.

        Pure Python -- trigger P10 (L-09/L-10: the fixture creates
        an ``account.account`` record via ``env.ref`` for the
        account type, which the ``EVAL:`` sandbox cannot express).
        """
        account_type = self.env.ref("account.data_account_type_expenses")
        account = self.env["account.account"].create(
            {
                "name": "Account Constrain 2",
                "code": "5199.91",
                "user_type_id": account_type.id,
            }
        )
        self.env["school_budget_expense_category"].create(
            {
                "name": "Expense Constrain Account 3",
                "code": "5160.92",
                "account_id": account.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_income_category"].create(
                {
                    "name": "Income Constrain Account 1",
                    "code": "4130.90",
                    "calc_method": "manual",
                    "account_id": account.id,
                }
            )
