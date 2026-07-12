# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetOldAsset(models.Model):
    """
    Represents a fixed asset acquired in a previous fiscal year and
    still being depreciated within a school_budget document's
    fiscal year. Depreciation is computed straight-line based on
    the number of years elapsed since acquisition.
    """

    _name = "school_budget_old_asset"
    _description = "School Budget Old Asset"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this old asset belongs to.",
    )
    asset_code = fields.Char(
        string="Asset Code",
    )
    asset_name = fields.Char(
        string="Asset Name",
        required=True,
    )
    acquisition_cost = fields.Monetary(
        string="Acquisition Cost",
        required=True,
        currency_field="currency_id",
    )
    useful_life = fields.Integer(
        string="Useful Life (Years)",
        required=True,
    )
    acquisition_year = fields.Integer(
        string="Acquisition Year",
        required=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )
    fiscal_year = fields.Integer(
        string="Fiscal Year",
        related="budget_id.fiscal_year",
        store=True,
        compute_sudo=True,
        help="The budget's fiscal year, used to compute the elapsed "
        "depreciation years.",
    )
    dep_per_year = fields.Monetary(
        string="Depreciation Per Year",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="acquisition_cost / useful_life.",
    )
    dep_current_year = fields.Monetary(
        string="Depreciation Current Year",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="dep_per_year if the asset is still within its useful "
        "life this fiscal year, otherwise 0.",
    )
    book_value = fields.Monetary(
        string="Book Value",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="max(0, acquisition_cost - dep_per_year * years elapsed).",
    )

    @api.depends("acquisition_cost", "useful_life", "acquisition_year", "fiscal_year")
    def _compute_depreciation(self):
        for record in self:
            if record.useful_life and record.useful_life > 0:
                dep_per_year = record.acquisition_cost / record.useful_life
            else:
                dep_per_year = 0.0
            fiscal_year = record.fiscal_year or 0
            acquisition_year = record.acquisition_year or 0
            year_number = fiscal_year - acquisition_year + 1
            if year_number < 1 or year_number > record.useful_life:
                dep_current_year = 0.0
            else:
                dep_current_year = dep_per_year
            book_value = max(
                0.0,
                record.acquisition_cost - dep_per_year * (fiscal_year - acquisition_year),
            )
            record.dep_per_year = dep_per_year
            record.dep_current_year = dep_current_year
            record.book_value = book_value

    @api.constrains("acquisition_cost", "useful_life", "acquisition_year")
    def _check_old_asset_values(self):
        for record in self.sudo():
            if not record._check_old_asset_values_condition():
                error_message = (
                    _(
                        """
Context: Save school budget old asset
Database ID: %s
Problem: Acquisition Cost must be greater than zero, Useful Life
must be at least 1, and Acquisition Year must be between 1900 and
2100
Solution: Correct the values
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_old_asset_values_condition(self):
        self.ensure_one()
        return (
            self.acquisition_cost > 0
            and self.useful_life >= 1
            and 1900 <= self.acquisition_year <= 2100
        )
