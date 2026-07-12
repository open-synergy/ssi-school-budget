# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetFinancialInvestment(models.Model):
    """
    Represents a financial instrument (stock, mutual fund, bond,
    time deposit, ...) held by a branch or center school_budget
    document. Financial investments enter a unit's UP cost base as
    a full nominal amount via the allocation mechanism
    (ssi_school_budget) — they are never depreciated.
    """

    _name = "school_budget_financial_investment"
    _description = "School Budget Financial Investment"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The branch/center budget document holding this " "financial investment.",
    )
    instrument_type = fields.Selection(
        string="Instrument Type",
        selection=[
            ("saham", "Stock"),
            ("reksa_dana", "Mutual Fund"),
            ("obligasi", "Bond"),
            ("deposito", "Time Deposit"),
            ("lainnya", "Other"),
        ],
        required=True,
        help="Type of financial instrument.",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id",
        help="Full nominal amount. Never depreciated.",
    )
    note = fields.Text(
        string="Note",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )

    @api.constrains("budget_id", "amount")
    def _check_org_type(self):
        for record in self.sudo():
            if not record._check_org_type_condition():
                error_message = (
                    _(
                        """
Context: Save school budget financial investment
Database ID: %s
Problem: Financial investments are only allowed on branch or center
budgets, with a positive Amount
Solution: Select a branch/center budget and enter an Amount greater
than zero
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_org_type_condition(self):
        self.ensure_one()
        return self.budget_id.org_type in ("branch", "center") and self.amount > 0
