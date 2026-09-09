# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetExpenseLine(models.Model):
    """
    Represents a single budgeted expense item under a school_budget
    document. Amounts are split between foundation-funded and
    BOS-funded (government) money because the tariff simulation
    engine (ssi_school_budget) treats the two differently: the UP/US
    cost base uses foundation+bos, while direct income only uses
    foundation.
    """

    _name = "school_budget_expense_line"
    _description = "School Budget Expense Line"
    _order = "expense_category_id, line_number, id"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this expense line belongs to.",
    )
    expense_category_id = fields.Many2one(
        string="Expense Category",
        comodel_name="school_budget_expense_category",
        required=True,
        help="The expense category this line is budgeted under.",
    )
    line_number = fields.Integer(
        string="Line Number",
        default=1,
        required=True,
        help="Ordering number of this line within its category. "
        "Must be 1 or greater.",
    )
    description = fields.Char(
        string="Description",
        help="Free-text description of this expense item.",
    )
    basis = fields.Char(
        string="Basis",
        help="Free-text calculation basis, e.g. '24 x 12 x Rp 3,500,000'.",
    )
    foundation = fields.Monetary(
        string="Foundation",
        default=0.0,
        currency_field="currency_id",
        help="Amount funded by the foundation (Yayasan).",
    )
    bos = fields.Monetary(
        string="BOS",
        default=0.0,
        currency_field="currency_id",
        help="Amount funded by government BOS/BOP/PBOS subsidy.",
    )
    amount_total = fields.Monetary(
        string="Total",
        compute="_compute_amount_total",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Foundation amount plus BOS amount.",
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
    is_operational = fields.Boolean(
        string="Operational",
        related="expense_category_id.is_operational",
        store=True,
        compute_sudo=True,
    )
    is_up_component = fields.Boolean(
        string="UP Component",
        related="expense_category_id.is_up_component",
        store=True,
        compute_sudo=True,
    )
    is_direct_income = fields.Boolean(
        string="Direct Income",
        related="expense_category_id.is_direct_income",
        store=True,
        compute_sudo=True,
    )
    grade_allocation_ids = fields.One2many(
        string="Grade Allocations",
        comodel_name="school_budget_expense_grade_allocation",
        inverse_name="line_id",
        help="Split of this expense line's direct income across "
        "grades, used when the target income category is "
        "grade-based.",
    )

    @api.depends("foundation", "bos")
    def _compute_amount_total(self):
        """Sum ``foundation`` and ``bos`` into ``amount_total``."""
        for record in self:
            record.amount_total = record.foundation + record.bos

    @api.constrains("line_number")
    def _check_line_number(self):
        """Reject a line number below 1.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_line_number_condition():
                error_message = (
                    _(
                        """
Context: Save school budget expense line
Database ID: %s
Problem: Line Number must be 1 or greater
Solution: Enter a value of 1 or more
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_line_number_condition(self):
        """Return whether ``line_number`` is 1 or greater.

        :return: ``True`` when ``line_number`` >= 1
        """
        self.ensure_one()
        return self.line_number >= 1
