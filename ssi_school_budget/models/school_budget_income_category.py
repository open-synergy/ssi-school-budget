# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetIncomeCategory(models.Model):
    """
    Represents a category of budgeted income (e.g. UP, US, BOS,
    manual income). The ``calc_method`` field determines how the
    simulation engine (ssi_school_budget) computes the amount booked
    under this category: either taken automatically from the UP/US
    tariff simulation, from BOS-funded expense/investment lines,
    derived from a direct-income expense category, allocated per
    grade, or entered manually by the user.
    """

    _name = "school_budget_income_category"
    _inherit = ["mixin.master_data"]
    _description = "School Budget Income Category"
    _order = "sequence asc, id"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        required=True,
        help="Display order of the category. Lower values appear first.",
    )
    calc_method = fields.Selection(
        string="Calculation Method",
        selection=[
            ("manual", "Manual"),
            ("simulated_up", "Simulated - Uang Pangkal (UP)"),
            ("simulated_us", "Simulated - Uang Sekolah (US)"),
            ("from_expense", "From Direct Income Expense Category"),
            ("grade_based", "Grade Based"),
            ("sum_from_bos", "Sum From BOS"),
        ],
        required=True,
        default="manual",
        help=(
            "How the simulation engine computes the amount for this "
            "income category:\n"
            "- Manual: entered directly by the user on the income line.\n"
            "- Simulated - UP: taken from the unit's computed UP "
            "(Uang Pangkal) tariff revenue.\n"
            "- Simulated - US: taken from the unit's computed US "
            "(Uang Sekolah) tariff revenue.\n"
            "- From Direct Income Expense Category: derived from the "
            "foundation-funded amount of expense lines whose category "
            "has 'Direct Income' enabled and maps to this category.\n"
            "- Grade Based: same as above, but split using the "
            "expense line's grade allocation when available.\n"
            "- Sum From BOS: the sum of the BOS-funded portion of "
            "all expense lines and investments in the budget."
        ),
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        domain=[("user_type_id.internal_group", "=", "income")],
        help="General ledger account used to pull the actual "
        "(realized) amount of this category from posted journal "
        "items. Leave empty when this category is not tracked "
        "against the ledger.",
    )

    @api.constrains("account_id")
    def _check_budget_account_unique(self):
        for record in self.sudo():
            if not record._check_budget_account_unique_condition():
                error_message = (
                    _(
                        """
Context: Save school budget income category
Database ID: %s
Problem: Account '%s' is already mapped to another category. Mapping
one account to two categories would count the same journal item
twice
Solution: Select an account that is not mapped elsewhere
"""
                    )
                    % (
                        record.id,
                        record.account_id.display_name,
                    )
                )
                raise ValidationError(error_message)

    def _check_budget_account_unique_condition(self):
        self.ensure_one()
        if not self.account_id:
            return True
        account_id = self.account_id.id
        if self.search_count(
            [("account_id", "=", account_id), ("id", "!=", self.id)]
        ):
            return False
        if self.env["school_budget_expense_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        if self.env["school_budget_investment_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        return True
