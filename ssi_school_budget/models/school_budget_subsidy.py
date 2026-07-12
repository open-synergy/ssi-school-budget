# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetSubsidy(models.Model):
    """
    Represents a direct transfer from a branch/center budget
    (provider) to another organization's budget (recipient): booked
    as an expense at the provider and as income at the recipient.
    Unlike parent expense allocation, a subsidy does NOT enter the
    recipient's UP/US cost base — it is purely additional income.
    """

    _name = "school_budget_subsidy"
    _description = "School Budget Subsidy"

    provider_budget_id = fields.Many2one(
        string="# Provider Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The branch/center budget document giving the subsidy.",
    )
    recipient_budget_id = fields.Many2one(
        string="Recipient Budget",
        comodel_name="school_budget",
        required=True,
        help="The budget document receiving the subsidy. A branch "
        "may only subsidize its own units; a center may subsidize "
        "any branch or unit.",
    )
    expense_category_id = fields.Many2one(
        string="Expense Category",
        comodel_name="school_budget_expense_category",
        required=True,
        help="The expense category booked at the provider.",
    )
    income_category_id = fields.Many2one(
        string="Income Category",
        comodel_name="school_budget_income_category",
        required=True,
        help="The income category booked at the recipient.",
    )
    amount = fields.Monetary(
        string="Amount",
        required=True,
        default=0.0,
        currency_field="currency_id",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="provider_budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )

    @api.constrains("provider_budget_id", "recipient_budget_id", "amount")
    def _check_subsidy_relation(self):
        for record in self.sudo():
            if not record._check_subsidy_relation_condition():
                error_message = (
                    _(
                        """
Context: Save school budget subsidy
Database ID: %s
Problem: Invalid provider/recipient relationship for this subsidy
Solution: Provider must be a branch or center budget, different
from the recipient. A branch may only subsidize its own units. A
center may subsidize any branch or unit (but not another center).
Provider and recipient must share the same academic year, and Amount
must not be negative
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_subsidy_relation_condition(self):
        self.ensure_one()
        provider = self.provider_budget_id
        recipient = self.recipient_budget_id
        if provider.org_type not in ("branch", "center"):
            return False
        if provider == recipient:
            return False
        if recipient.org_type == "center":
            return False
        if provider.academic_year_id != recipient.academic_year_id:
            return False
        if self.amount < 0:
            return False
        if provider.org_type == "branch":
            if recipient.org_type != "unit":
                return False
            if recipient.school_id.branch_id != provider.branch_id:
                return False
        # provider.org_type == "center": branch or unit within the
        # same company is allowed, already implied by the search
        # domain used by the ORM (no operating unit is involved).
        return True
