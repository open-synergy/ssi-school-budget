# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetIncomeLine(models.Model):
    """
    Represents a manually entered budgeted income item under a
    school_budget document. Only income categories with
    calc_method=manual may be booked here; every other calculation
    method is produced automatically by the simulation engine
    (ssi_school_budget).
    """

    _name = "school_budget_income_line"
    _description = "School Budget Income Line"
    _order = "income_category_id, line_number, id"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this income line belongs to.",
    )
    income_category_id = fields.Many2one(
        string="Income Category",
        comodel_name="school_budget_income_category",
        required=True,
        help="The income category this line is budgeted under. Only "
        "categories with Calculation Method = Manual are allowed.",
    )
    line_number = fields.Integer(
        string="Line Number",
        default=1,
        help="Ordering number of this line within its category.",
    )
    description = fields.Char(
        string="Description",
        help="Free-text description of this income item.",
    )
    basis = fields.Char(
        string="Basis",
        help="Free-text calculation basis.",
    )
    amount = fields.Monetary(
        string="Amount",
        default=0.0,
        currency_field="currency_id",
        help="Manually entered budgeted income amount.",
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

    @api.constrains("income_category_id")
    def _check_manual_income_category(self):
        """Reject a non-manual income category on a manual line.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_manual_income_category_condition():
                error_message = (
                    _(
                        """
Context: Save school budget income line
Database ID: %s
Problem: This income category is calculated automatically by the
simulation and cannot be entered manually
Solution: Select an income category whose Calculation Method is
Manual
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_manual_income_category_condition(self):
        """Return whether the income category's calc_method is manual.

        :return: ``True`` when ``income_category_id`` is empty or
            its ``calc_method`` is ``manual``
        """
        self.ensure_one()
        if not self.income_category_id:
            return True
        return self.income_category_id.calc_method == "manual"
