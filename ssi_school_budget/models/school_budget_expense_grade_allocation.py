# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolBudgetExpenseGradeAllocation(models.Model):
    """
    Splits a single school_budget_expense_line's direct income
    amount across grades. Only relevant when the expense line's
    category is a direct-income category whose target income
    category has calc_method=grade_based (ssi_school_budget).
    """

    _name = "school_budget_expense_grade_allocation"
    _description = "School Budget Expense Grade Allocation"
    _order = "line_id, grade_id"

    line_id = fields.Many2one(
        string="# Expense Line",
        comodel_name="school_budget_expense_line",
        required=True,
        ondelete="cascade",
        help="The expense line this grade allocation belongs to.",
    )
    grade_id = fields.Many2one(
        string="Grade",
        comodel_name="school_grade",
        required=True,
        help="The grade this allocated amount applies to.",
    )
    amount = fields.Monetary(
        string="Amount",
        default=0.0,
        currency_field="currency_id",
        help="Direct income amount allocated to this grade.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="line_id.currency_id",
        store=True,
        compute_sudo=True,
    )

    _sql_constraints = [
        (
            "unique_line_grade",
            "unique(line_id, grade_id)",
            "Only one grade allocation is allowed per grade on the "
            "same expense line.",
        ),
    ]
