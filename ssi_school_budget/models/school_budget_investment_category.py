# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetInvestmentCategory(models.Model):
    """
    Represents a category of budgeted fixed-asset investment (e.g.
    furniture, IT equipment). Provides the default useful life
    (in years) used to prefill new investment lines in
    ssi_school_budget.
    """

    _name = "school_budget_investment_category"
    _inherit = ["mixin.master_data"]
    _description = "School Budget Investment Category"
    _order = "sequence asc, id"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        required=True,
        help="Display order of the category. Lower values appear first.",
    )
    default_economic_life = fields.Integer(
        string="Default Economic Life (Years)",
        default=4,
        required=True,
        help=(
            "Default useful life, in years, used to prefill new "
            "investment lines under this category. Must be greater "
            "than zero."
        ),
    )

    @api.constrains("default_economic_life")
    def _check_default_economic_life(self):
        """Reject a non-positive default economic life.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_default_economic_life_condition():
                error_message = (
                    _(
                        """
Context: Save school budget investment category
Database ID: %s
Problem: Default Economic Life must be greater than zero
Solution: Enter a value of 1 or more
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_default_economic_life_condition(self):
        """Return whether ``default_economic_life`` is positive.

        :return: ``True`` when ``default_economic_life`` > 0
        """
        self.ensure_one()
        return self.default_economic_life > 0

    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        domain=[("user_type_id.internal_group", "=", "asset")],
        help="General ledger account used to pull the actual "
        "(realized) amount of this category from posted journal "
        "items. Leave empty when this category is not tracked "
        "against the ledger.",
    )

    @api.constrains("account_id")
    def _check_budget_account_unique(self):
        """Reject an account already mapped to another category.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_budget_account_unique_condition():
                error_message = (
                    _(
                        """
Context: Save school budget investment category
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
        """Return whether ``account_id`` is unique across categories.

        Checks against other investment categories, expense
        categories, and income categories.

        :return: ``True`` when the account is empty or not mapped
            elsewhere
        """
        self.ensure_one()
        if not self.account_id:
            return True
        account_id = self.account_id.id
        if self.search_count([("account_id", "=", account_id), ("id", "!=", self.id)]):
            return False
        if self.env["school_budget_expense_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        if self.env["school_budget_income_category"].search_count(
            [("account_id", "=", account_id)]
        ):
            return False
        return True
