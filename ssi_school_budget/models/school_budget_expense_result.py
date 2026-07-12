# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolBudgetExpenseResult(models.Model):
    """
    A single generated expense line of a school_budget document,
    produced by action_simulate() (ssi_school_budget). Rows are
    read-only for users; they are deleted and rewritten as a whole
    every time the simulation runs.
    """

    _name = "school_budget_expense_result"
    _description = "School Budget Expense Result"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        help="The budget document this generated expense line " "belongs to.",
    )
    expense_category_id = fields.Many2one(
        string="Expense Category",
        comodel_name="school_budget_expense_category",
        help="The expense category this line was generated for. "
        "Empty for synthetic rows that have no category equivalent.",
    )
    code = fields.Char(
        string="Code",
    )
    label = fields.Char(
        string="Label",
    )
    amount_foundation = fields.Monetary(
        string="Foundation",
        currency_field="currency_id",
    )
    amount_bos = fields.Monetary(
        string="BOS",
        currency_field="currency_id",
    )
    amount_total = fields.Monetary(
        string="Total",
        currency_field="currency_id",
    )
    expense_group = fields.Selection(
        string="Expense Group",
        selection=[
            ("operational", "Operational"),
            ("non_operational", "Non Operational"),
        ],
    )
    source = fields.Selection(
        string="Source",
        selection=[
            ("own", "Own"),
            ("subsidy_given", "Subsidy Given"),
            ("allocated_up", "Allocated UP"),
            ("allocated_us", "Allocated US"),
            ("allocated_dep_new", "Allocated New Investment Depreciation"),
            ("allocated_dep_old", "Allocated Old Asset Depreciation"),
            ("allocated_financial_investment", "Allocated Financial Investment"),
        ],
        help="How this line's amount was derived.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )
