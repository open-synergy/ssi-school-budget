# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetInvestment(models.Model):
    """
    Represents a new fixed-asset investment planned within a
    school_budget document's fiscal year. Depreciation is computed
    straight-line, prorated by start month. The BOS-funded portion
    (bos) deliberately does NOT reduce the depreciable base — the
    reference application always depreciates the full purchase
    price.
    """

    _name = "school_budget_investment"
    _description = "School Budget Investment"

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The budget document this investment belongs to.",
    )
    investment_category_id = fields.Many2one(
        string="Investment Category",
        comodel_name="school_budget_investment_category",
        required=True,
        help="The investment category, used to prefill Useful Life.",
    )
    asset_code = fields.Char(
        string="Asset Code",
    )
    asset_name = fields.Char(
        string="Asset Name",
        required=True,
    )
    purchase_price = fields.Monetary(
        string="Purchase Price",
        required=True,
        currency_field="currency_id",
        help="Full purchase price. Always used as the depreciable "
        "base, regardless of the BOS-funded portion.",
    )
    bos = fields.Monetary(
        string="BOS",
        default=0.0,
        currency_field="currency_id",
        help="Portion of the purchase price funded by government "
        "BOS/BOP/PBOS subsidy. Does NOT reduce the depreciable base.",
    )
    useful_life = fields.Integer(
        string="Useful Life (Years)",
        required=True,
        help="Useful life in years.",
    )
    start_month = fields.Integer(
        string="Start Month",
        required=True,
        default=1,
        help="Month (1-12) the asset starts being used, for "
        "prorated first-year depreciation.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="budget_id.currency_id",
        store=True,
        compute_sudo=True,
    )
    dep_per_year = fields.Monetary(
        string="Depreciation Per Year",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="purchase_price / useful_life (0 when useful_life <= 0).",
    )
    dep_current_year = fields.Monetary(
        string="Depreciation Current Year",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="dep_per_year * (13 - start_month) / 12, start_month " "clamped to 1..12.",
    )
    end_book_value = fields.Monetary(
        string="End Book Value",
        compute="_compute_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="purchase_price - dep_current_year.",
    )

    @api.depends("purchase_price", "useful_life", "start_month")
    def _compute_depreciation(self):
        """Straight-line depreciation, prorated for the start month.

        Fills ``dep_per_year``, ``dep_current_year`` (prorated by
        ``13 - start_month`` over 12 months), and ``end_book_value``.
        """
        for record in self:
            if record.useful_life and record.useful_life > 0:
                dep_per_year = record.purchase_price / record.useful_life
            else:
                dep_per_year = 0.0
            start_month = min(max(record.start_month or 1, 1), 12)
            dep_current_year = dep_per_year * (13 - start_month) / 12
            record.dep_per_year = dep_per_year
            record.dep_current_year = dep_current_year
            record.end_book_value = record.purchase_price - dep_current_year

    @api.onchange("investment_category_id")
    def onchange_useful_life(self):
        if self.investment_category_id and not self.useful_life:
            self.useful_life = self.investment_category_id.default_economic_life

    @api.constrains("purchase_price", "useful_life", "start_month")
    def _check_investment_values(self):
        """Reject invalid purchase price, useful life, or start month.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_investment_values_condition():
                error_message = (
                    _(
                        """
Context: Save school budget investment
Database ID: %s
Problem: Purchase Price must be greater than zero, Useful Life must
be at least 1, and Start Month must be between 1 and 12
Solution: Correct the values
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_investment_values_condition(self):
        """Return whether purchase price/useful life/start month are valid.

        :return: ``True`` when ``purchase_price`` > 0, ``useful_life``
            >= 1, and ``start_month`` is between 1 and 12
        """
        self.ensure_one()
        return (
            self.purchase_price > 0
            and self.useful_life >= 1
            and 1 <= self.start_month <= 12
        )
