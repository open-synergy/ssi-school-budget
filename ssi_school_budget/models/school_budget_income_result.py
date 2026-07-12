# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolBudgetIncomeResult(models.Model):
    """
    A single generated income line of a school_budget document,
    produced by action_simulate() (ssi_school_budget). Rows are
    read-only for users; they are deleted and rewritten as a whole
    every time the simulation runs, so they can be safely compared
    against realization (budget vs actual) and printed on reports.
    """

    _name = "school_budget_income_result"
    _description = "School Budget Income Result"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        help="The budget document this generated income line "
        "belongs to.",
    )
    income_category_id = fields.Many2one(
        string="Income Category",
        comodel_name="school_budget_income_category",
        help="The income category this line was generated for. "
        "Empty for synthetic rows that have no category equivalent.",
    )
    code = fields.Char(
        string="Code",
    )
    label = fields.Char(
        string="Label",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        help="Final amount, honoring any applicable override.",
    )
    auto_amount = fields.Monetary(
        string="Auto Amount",
        currency_field="currency_id",
        help="Automatically computed amount, ignoring overrides.",
    )
    source = fields.Selection(
        string="Source",
        selection=[
            ("simulated_up", "Simulated UP"),
            ("simulated_us", "Simulated US"),
            ("direct_income", "Direct Income"),
            ("bos", "BOS"),
            ("manual", "Manual"),
            ("contribution_up", "Contribution UP"),
            ("contribution_us", "Contribution US"),
            ("subsidy", "Subsidy"),
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
