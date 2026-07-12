# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetExpenseCategory(models.Model):
    """
    Represents a category of budgeted expense (e.g. teacher
    salaries, facility maintenance). Flags on this category steer
    the simulation engine (ssi_school_budget): whether the expense
    is operational, whether it contributes to the UP (Uang Pangkal)
    cost base, and whether it directly produces income booked under
    another income category.
    """

    _name = "school_budget_expense_category"
    _inherit = ["mixin.master_data"]
    _description = "School Budget Expense Category"
    _order = "sequence asc, id"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        required=True,
        help="Display order of the category. Lower values appear first.",
    )
    is_operational = fields.Boolean(
        string="Operational",
        default=True,
        help=(
            "When enabled, this category represents an operational "
            "expense (e.g. account range 5110-5250). When disabled, "
            "it is a non-operational expense (e.g. account range "
            "5500-5590)."
        ),
    )
    is_up_component = fields.Boolean(
        string="UP Component",
        default=False,
        help=(
            "When enabled, expense lines under this category are "
            "included in the UP (Uang Pangkal) cost base used by the "
            "tariff simulation engine."
        ),
    )
    is_direct_income = fields.Boolean(
        string="Direct Income",
        default=False,
        help=(
            "When enabled, expense lines under this category "
            "automatically generate a matching income line (based on "
            "the foundation-funded amount) booked under "
            "'Maps to Income Category'."
        ),
    )
    maps_to_income_category_id = fields.Many2one(
        string="Maps to Income Category",
        comodel_name="school_budget_income_category",
        help=(
            "The income category that receives the direct income "
            "amount generated from this expense category. Required "
            "when 'Direct Income' is enabled."
        ),
    )
    contribution_role = fields.Char(
        string="Contribution Role",
        help=(
            "Free-text label describing the role of this category in "
            "the parent-child contribution mechanism, e.g. "
            "'up_to_pusat', 'subsidy_to_unit'. Informational only."
        ),
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        domain=[("user_type_id.internal_group", "=", "expense")],
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
Context: Save school budget expense category
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
        if self.search_count([("account_id", "=", account_id), ("id", "!=", self.id)]):
            return False
        if self.env["school_budget_income_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        if self.env["school_budget_investment_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        return True

    @api.constrains("is_direct_income", "maps_to_income_category_id")
    def _check_direct_income_target(self):
        for record in self.sudo():
            if not record._check_direct_income_target_condition():
                error_message = (
                    _(
                        """
Context: Save school budget expense category
Database ID: %s
Problem: 'Direct Income' is enabled but 'Maps to Income Category' is
empty
Solution: Select the income category that should receive the direct
income generated from this expense category
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_direct_income_target_condition(self):
        self.ensure_one()
        if not self.is_direct_income:
            return True
        return bool(self.maps_to_income_category_id)
