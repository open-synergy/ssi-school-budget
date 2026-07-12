# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo_yaml_test import YamlTransactionCase


@tagged("post_install", "-at_install")
class TestSchoolBudgetInvestment(YamlTransactionCase):
    def test_school_budget_investment(self):
        self.run_yaml_scenario("test_data_school_budget_investment.yaml")

    def _setup_budget(self, suffix, org_type="unit"):
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "Grade Type Invest Constrain %s" % suffix,
                "code": "GTIC%s" % suffix,
                "sequence": 10,
            }
        )
        vals = {
            "org_type": org_type,
            "academic_year_id": self.env["school_academic_year"]
            .create(
                {
                    "name": "Year Invest Constrain %s" % suffix,
                    "code": "AYIC%s" % suffix,
                    "date_start": "2025-07-01",
                    "date_end": "2026-06-30",
                }
            )
            .id,
        }
        if org_type == "unit":
            school = self.env["school"].create(
                {
                    "name": "School Invest Constrain %s" % suffix,
                    "code": "SCHIC%s" % suffix,
                    "grade_type_id": grade_type.id,
                }
            )
            vals["school_id"] = school.id
        return self.env["school_budget"].create(vals)

    def test_constrain_investment_start_month_13_blocks_create(self):
        """start_month must be between 1 and 12."""
        budget = self._setup_budget("S1")
        investment_category = self.env["school_budget_investment_category"].create(
            {
                "name": "Investment Constrain S1",
                "code": "1330.91",
                "default_economic_life": 4,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["school_budget_investment"].create(
                {
                    "budget_id": budget.id,
                    "investment_category_id": investment_category.id,
                    "asset_name": "Bad Asset",
                    "purchase_price": 10000000,
                    "useful_life": 4,
                    "start_month": 13,
                }
            )

    def test_constrain_financial_investment_on_unit_budget_blocks_create(self):
        """Financial investments are not allowed on unit budgets."""
        budget = self._setup_budget("F1", org_type="unit")
        with self.assertRaises(ValidationError):
            self.env["school_budget_financial_investment"].create(
                {
                    "budget_id": budget.id,
                    "instrument_type": "deposito",
                    "name": "Bad Financial Investment",
                    "amount": 1000000,
                }
            )
