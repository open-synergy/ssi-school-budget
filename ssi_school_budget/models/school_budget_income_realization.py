# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolBudgetIncomeRealization(models.Model):
    """
    Monthly realized (actual) income amount of a single income
    category, pulled from posted account.move.line entries by
    action_compute_realization() (ssi_school_budget). Read-only for
    users; deleted and rewritten as a whole every time realization
    is recomputed.
    """

    _name = "school_budget_income_realization"
    _description = "School Budget Income Realization"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        help="The budget document this realization line belongs to.",
    )
    income_category_id = fields.Many2one(
        string="Income Category",
        comodel_name="school_budget_income_category",
        required=True,
    )
    month = fields.Integer(
        string="Month",
        required=True,
        help="Month index, 1-12, relative to the academic year's "
        "start month (month 1 = the calendar month "
        "academic_year_id.date_start falls in), not the calendar "
        "year.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )

    _sql_constraints = [
        (
            "unique_budget_category_month",
            "unique(budget_id, income_category_id, month)",
            "Only one realization row is allowed per category and "
            "month on the same budget.",
        ),
    ]
