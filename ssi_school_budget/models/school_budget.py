# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolBudget(models.Model):
    """
    Represents the yearly budget (RAB) document of a single
    organization (a school unit, a branch, or the center/company).
    One record exists per (organization, academic year) pair and
    acts as the anchor that every other school budget detail model
    (assumption, expense/income line, investment, allocation,
    simulation result, realization, ...) points to via budget_id.
    The lock/unlock mechanism of the reference application is
    replaced by the standard SSI document state: draft (free input)
    -> confirm (pending approval) -> done (locked), plus cancel.
    """

    _name = "school_budget"
    _description = "School Budget"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    date = fields.Date(
        string="Date",
        default=lambda r: datetime_date.today(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The document date, used by the sequence template.",
    )
    org_type = fields.Selection(
        string="Organization Type",
        selection=[
            ("unit", "Unit"),
            ("branch", "Branch"),
            ("center", "Center"),
        ],
        required=True,
        default="unit",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help=(
            "The organization level this budget belongs to: a school "
            "Unit, a Branch, or the Center (company)."
        ),
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The school unit this budget belongs to. Required when "
        "Organization Type is Unit.",
    )
    branch_id = fields.Many2one(
        string="Branch",
        comodel_name="school_branch",
        compute="_compute_branch_id",
        store=True,
        compute_sudo=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help=(
            "The branch this budget belongs to. When Organization "
            "Type is Unit, this is automatically derived from the "
            "school's branch. Required when Organization Type is "
            "Branch."
        ),
    )
    # company_id is already provided by mixin.transaction (required,
    # defaults to the current user's company).
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The academic year this budget plans for.",
    )
    fiscal_year = fields.Integer(
        string="Fiscal Year",
        compute="_compute_fiscal_year",
        store=True,
        compute_sudo=True,
        help=(
            "The calendar year the academic year starts in. Used by "
            "all depreciation computations in this budget."
        ),
    )
    cash_balance = fields.Monetary(
        string="Opening Cash Balance",
        default=0.0,
        currency_field="currency_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Cash and cash-equivalent balance at the start of the " "budget period.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="company_id.currency_id",
        store=True,
        compute_sudo=True,
    )
    assumption_line_ids = fields.One2many(
        string="Student Assumption Lines",
        comodel_name="school_budget_assumption_line",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Planned student headcount per grade (org_type=unit only).",
    )
    total_student_count = fields.Integer(
        string="Total Student Count",
        compute="_compute_total_student_count",
        store=True,
        compute_sudo=True,
        help=(
            "Sum of student_count across all assumption lines. Used "
            "as the divisor of the US tariff simulation."
        ),
    )
    new_student_count = fields.Integer(
        string="New Student Count",
        default=0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Number of new students. Used as the divisor of the UP "
        "tariff simulation.",
    )
    returning_student_count = fields.Integer(
        string="Returning Student Count",
        default=0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Number of returning students. Informational only.",
    )
    staff_count = fields.Integer(
        string="Staff Count",
        default=0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Number of staff. Informational only.",
    )
    is_up_rate_overridden = fields.Boolean(
        string="Override UP Rate",
        default=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help=(
            "When enabled, Override UP Rate is used as the final UP "
            "tariff instead of the automatically computed rate. This "
            "boolean is the substitute for the reference "
            "application's 'None = automatic' semantics: an override "
            "value of zero is only honored when this box is checked."
        ),
    )
    override_up_rate = fields.Monetary(
        string="Override UP Rate",
        default=0.0,
        currency_field="currency_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Manually forced UP tariff. Only used when 'Override UP "
        "Rate' is enabled.",
    )
    is_us_rate_overridden = fields.Boolean(
        string="Override US Rate",
        default=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help=(
            "When enabled, Override US Rate is used as the final US "
            "tariff instead of the automatically computed rate. This "
            "boolean is the substitute for the reference "
            "application's 'None = automatic' semantics: an override "
            "value of zero is only honored when this box is checked."
        ),
    )
    override_us_rate = fields.Monetary(
        string="Override US Rate",
        default=0.0,
        currency_field="currency_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Manually forced US tariff. Only used when 'Override US "
        "Rate' is enabled.",
    )

    expense_line_ids = fields.One2many(
        string="Expense Lines",
        comodel_name="school_budget_expense_line",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Budgeted expense items.",
    )
    income_line_ids = fields.One2many(
        string="Income Lines",
        comodel_name="school_budget_income_line",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Manually budgeted income items (calc_method=manual only).",
    )
    total_expense_foundation = fields.Monetary(
        string="Total Expense (Foundation)",
        compute="_compute_total_expense",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the Foundation column across all expense lines.",
    )
    total_expense_bos = fields.Monetary(
        string="Total Expense (BOS)",
        compute="_compute_total_expense",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the BOS column across all expense lines.",
    )
    total_expense = fields.Monetary(
        string="Total Expense",
        compute="_compute_total_expense",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of amount_total across all expense lines.",
    )
    total_income_manual = fields.Monetary(
        string="Total Manual Income",
        compute="_compute_total_income_manual",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of amount across all manually entered income lines.",
    )

    @api.depends(
        "expense_line_ids.foundation",
        "expense_line_ids.bos",
        "expense_line_ids.amount_total",
    )
    def _compute_total_expense(self):
        """Sum expense line amounts into the expense totals.

        Fills ``total_expense_foundation``, ``total_expense_bos``,
        and ``total_expense`` from ``expense_line_ids``.
        """
        for record in self:
            record.total_expense_foundation = sum(
                record.expense_line_ids.mapped("foundation")
            )
            record.total_expense_bos = sum(record.expense_line_ids.mapped("bos"))
            record.total_expense = sum(record.expense_line_ids.mapped("amount_total"))

    @api.depends("income_line_ids.amount")
    def _compute_total_income_manual(self):
        """Sum ``income_line_ids.amount`` into total_income_manual."""
        for record in self:
            record.total_income_manual = sum(record.income_line_ids.mapped("amount"))

    investment_ids = fields.One2many(
        string="Investments",
        comodel_name="school_budget_investment",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="New fixed-asset investments planned this fiscal year.",
    )
    old_asset_ids = fields.One2many(
        string="Old Assets",
        comodel_name="school_budget_old_asset",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Fixed assets acquired in a previous fiscal year, still "
        "being depreciated.",
    )
    financial_investment_ids = fields.One2many(
        string="Financial Investments",
        comodel_name="school_budget_financial_investment",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Financial instruments held (branch/center only).",
    )
    total_new_investment_dep = fields.Monetary(
        string="Total New Investment Depreciation",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of dep_current_year across all new investments.",
    )
    total_old_asset_dep = fields.Monetary(
        string="Total Old Asset Depreciation",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of dep_current_year across all old assets.",
    )
    total_depreciation = fields.Monetary(
        string="Total Depreciation",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="total_new_investment_dep + total_old_asset_dep.",
    )
    total_physical_investment = fields.Monetary(
        string="Total Physical Investment",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of purchase_price across all new investments.",
    )
    total_financial_investment = fields.Monetary(
        string="Total Financial Investment",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of amount across all financial investments.",
    )
    total_investment = fields.Monetary(
        string="Total Investment",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="total_physical_investment + total_financial_investment.",
    )
    total_investment_bos = fields.Monetary(
        string="Total Investment BOS",
        compute="_compute_total_depreciation",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of bos across all new investments.",
    )

    @api.depends(
        "investment_ids.dep_current_year",
        "investment_ids.purchase_price",
        "investment_ids.bos",
        "old_asset_ids.dep_current_year",
        "financial_investment_ids.amount",
    )
    def _compute_total_depreciation(self):
        """Sum new-investment and old-asset depreciation totals.

        Fills ``total_new_investment_dep``, ``total_old_asset_dep``,
        ``total_depreciation``, ``total_physical_investment``, and
        ``total_financial_investment``.
        """
        for record in self:
            record.total_new_investment_dep = sum(
                record.investment_ids.mapped("dep_current_year")
            )
            record.total_old_asset_dep = sum(
                record.old_asset_ids.mapped("dep_current_year")
            )
            record.total_depreciation = (
                record.total_new_investment_dep + record.total_old_asset_dep
            )
            record.total_physical_investment = sum(
                record.investment_ids.mapped("purchase_price")
            )
            record.total_financial_investment = sum(
                record.financial_investment_ids.mapped("amount")
            )
            record.total_investment = (
                record.total_physical_investment + record.total_financial_investment
            )
            record.total_investment_bos = sum(record.investment_ids.mapped("bos"))

    parent_expense_allocation_ids = fields.One2many(
        string="Parent Expense Allocations",
        comodel_name="school_budget_parent_expense_allocation",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Expense categories of this branch/center budget that "
        "are pushed down into children's cost base.",
    )
    contribution_allocation_ids = fields.One2many(
        string="Contribution Allocations",
        comodel_name="school_budget_contribution_allocation",
        inverse_name="parent_budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Units contributing to this branch/center budget, with "
        "their proportion keys.",
    )

    def _get_ancestor_budgets(self):
        self.ensure_one()
        ancestors = self.env["school_budget"]
        if self.org_type == "unit" and self.branch_id:
            ancestors += self._find_ancestor_budget(
                "branch", branch_id=self.branch_id.id
            )
        if self.org_type in ("unit", "branch"):
            ancestors += self._find_ancestor_budget("center")
        return ancestors

    def _find_ancestor_budget(self, org_type, branch_id=None):
        self.ensure_one()
        domain = [
            ("org_type", "=", org_type),
            ("academic_year_id", "=", self.academic_year_id.id),
            ("company_id", "=", self.company_id.id),
            ("state", "!=", "cancel"),
        ]
        if branch_id:
            domain.append(("branch_id", "=", branch_id))
        return self.search(domain, limit=1)

    def action_sync_contribution_allocation(self):
        for record in self.sudo():
            record._sync_contribution_allocation()

    def _sync_contribution_allocation(self):
        self.ensure_one()
        allocation_model = self.env["school_budget_contribution_allocation"]
        for child in self._get_descendant_unit_budgets():
            allocation = self.contribution_allocation_ids.filtered(
                lambda a, child=child: a.child_budget_id == child
            )
            vals = {
                "total_student_count": child.total_student_count,
                "new_student_count": child.new_student_count,
            }
            if allocation:
                allocation.write(vals)
            else:
                allocation_model.create(
                    dict(
                        vals,
                        parent_budget_id=self.id,
                        child_budget_id=child.id,
                    )
                )

    def _get_descendant_unit_budgets(self):
        self.ensure_one()
        domain = [
            ("org_type", "=", "unit"),
            ("academic_year_id", "=", self.academic_year_id.id),
            ("company_id", "=", self.company_id.id),
            ("state", "!=", "cancel"),
        ]
        if self.org_type == "branch":
            domain.append(("branch_id", "=", self.branch_id.id))
        return self.search(domain)

    subsidy_ids = fields.One2many(
        string="Subsidies Given",
        comodel_name="school_budget_subsidy",
        inverse_name="provider_budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Subsidies given by this branch/center budget to other " "organizations.",
    )
    received_subsidy_ids = fields.One2many(
        string="Subsidies Received",
        comodel_name="school_budget_subsidy",
        inverse_name="recipient_budget_id",
        readonly=True,
        help="Subsidies received from provider organizations.",
    )
    direct_income_override_ids = fields.One2many(
        string="Direct Income Overrides",
        comodel_name="school_budget_direct_income_override",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Manual overrides of automatically computed direct " "income amounts.",
    )

    @api.depends("assumption_line_ids.student_count")
    def _compute_total_student_count(self):
        """Sum ``assumption_line_ids.student_count``."""
        for record in self:
            record.total_student_count = sum(
                record.assumption_line_ids.mapped("student_count")
            )

    @api.depends("org_type", "school_id", "school_id.branch_id")
    def _compute_branch_id(self):
        """Derive ``branch_id`` from the organization type.

        Unit budgets take the school's branch; center budgets have
        no branch; branch budgets keep the user-selected value.
        """
        for record in self:
            if record.org_type == "unit":
                record.branch_id = record.school_id.branch_id
            elif record.org_type == "center":
                record.branch_id = False
            else:
                # org_type == "branch": keep the user-selected value.
                record.branch_id = record.branch_id

    @api.depends("academic_year_id", "academic_year_id.date_start")
    def _compute_fiscal_year(self):
        """Derive the fiscal year from the academic year's start date."""
        for record in self:
            record.fiscal_year = (
                record.academic_year_id.date_start.year
                if record.academic_year_id and record.academic_year_id.date_start
                else False
            )

    @api.onchange("org_type")
    def onchange_school_id(self):
        if self.org_type != "unit":
            self.school_id = False

    @api.onchange("school_id")
    def onchange_assumption_line_ids(self):
        """Seed ``assumption_line_ids`` with the school's grades.

        Adds one new (unsaved) assumption line per grade of
        ``school_id.grade_type_id`` that does not already have a
        line, leaving existing lines untouched.
        """
        if not self.school_id or not self.school_id.grade_type_id:
            return
        existing_grade_ids = self.assumption_line_ids.mapped("grade_id").ids
        grades = self.env["school_grade"].search(
            [("type_id", "=", self.school_id.grade_type_id.id)]
        )
        new_lines = grades.filtered(lambda g: g.id not in existing_grade_ids)
        for grade in new_lines:
            self.assumption_line_ids = self.assumption_line_ids | self.env[
                "school_budget_assumption_line"
            ].new({"grade_id": grade.id, "student_count": 0})

    @api.constrains("new_student_count", "returning_student_count", "staff_count")
    def _check_assumption_counts(self):
        """Reject negative student/staff counts.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_assumption_counts_condition():
                error_message = (
                    _(
                        """
Context: Save school budget
Database ID: %s
Problem: New Student Count, Returning Student Count, or Staff Count
is negative
Solution: Enter zero or a positive number
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_assumption_counts_condition(self):
        """Return whether the assumption counts are non-negative.

        :return: ``True`` when ``new_student_count``,
            ``returning_student_count``, and ``staff_count`` are all
            >= 0
        """
        self.ensure_one()
        return (
            self.new_student_count >= 0
            and self.returning_student_count >= 0
            and self.staff_count >= 0
        )

    @api.constrains("org_type", "assumption_line_ids")
    def _check_assumption_org_type(self):
        """Reject assumption lines on a non-unit budget.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_assumption_org_type_condition():
                error_message = (
                    _(
                        """
Context: Save school budget
Database ID: %s
Problem: Student assumption lines are only allowed when Organization
Type is Unit
Solution: Remove the assumption lines, or change Organization Type
to Unit
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_assumption_org_type_condition(self):
        """Return whether assumption_line_ids matches org_type.

        :return: ``True`` when ``org_type`` is ``unit``, or when it
            is not ``unit`` and ``assumption_line_ids`` is empty
        """
        self.ensure_one()
        if self.org_type == "unit":
            return True
        return not self.assumption_line_ids

    @api.constrains("org_type", "school_id", "branch_id")
    def _check_organization(self):
        """Reject organization fields that do not match org_type.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_organization_condition():
                error_message = (
                    _(
                        """
Context: Save school budget
Database ID: %s
Problem: The organization fields do not match Organization Type '%s'
Solution: Unit requires School; Branch requires Branch (and no
School); Center requires neither School nor Branch to be set
"""
                    )
                    % (
                        record.id,
                        record.org_type,
                    )
                )
                raise ValidationError(error_message)

    def _check_organization_condition(self):
        """Return whether school_id/branch_id match org_type.

        :return: ``True`` when unit has ``school_id``, branch has
            ``branch_id`` without ``school_id``, or center has
            neither
        """
        self.ensure_one()
        if self.org_type == "unit":
            return bool(self.school_id)
        if self.org_type == "branch":
            return bool(self.branch_id) and not self.school_id
        # center
        return not self.school_id and not self.branch_id

    @api.constrains(
        "org_type", "school_id", "branch_id", "company_id", "academic_year_id"
    )
    def _check_unique_budget(self):
        """Reject a duplicate budget for the same org/year.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_unique_budget_condition():
                error_message = (
                    _(
                        """
Context: Save school budget
Database ID: %s
Problem: A budget for this organization and academic year already
exists
Solution: Edit the existing budget instead of creating a duplicate
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_unique_budget_condition(self):
        """Return whether this budget is unique for its org/year.

        A cancelled budget does not count as a duplicate, so a new
        one may be created in its place.

        :return: ``True`` when no other non-cancelled budget shares
            the same organization, company, and academic year
        """
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("org_type", "=", self.org_type),
            ("company_id", "=", self.company_id.id),
            ("academic_year_id", "=", self.academic_year_id.id),
            ("state", "!=", "cancel"),
        ]
        if self.org_type == "unit":
            domain.append(("school_id", "=", self.school_id.id))
        elif self.org_type == "branch":
            domain.append(("branch_id", "=", self.branch_id.id))
        return self.search_count(domain) == 0

    # ------------------------------------------------------------
    # UP / US tariff simulation engine (BL-0116)
    #
    # These fields are intentionally non-stored: their value depends
    # on ancestor budgets (branch/center) and sibling contribution
    # allocations, which are not modeled as Odoo dependency chains.
    # Tests must call invalidate_cache() before re-reading them after
    # a related record changes. Do NOT switch these to store=True.
    # ------------------------------------------------------------

    include_parent_allocation = fields.Boolean(
        string="Include Parent Allocation",
        default=True,
        help=(
            "When enabled (default), costs and depreciation pushed "
            "down from ancestor (branch/center) budgets are included "
            "in this unit's UP/US cost base. When disabled, every "
            "allocated component is treated as zero."
        ),
    )
    total_own_up_cost = fields.Monetary(
        string="Own UP Cost",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of (foundation + bos) of this unit's own expense "
        "lines whose category is a UP component.",
    )
    allocated_up_branch = fields.Monetary(
        string="Allocated UP Cost (Branch)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_up_center = fields.Monetary(
        string="Allocated UP Cost (Center)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_up_cost = fields.Monetary(
        string="Total UP Cost",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_own_up_cost + allocated_up_branch + allocated_up_center.",
    )
    own_new_investment_dep = fields.Monetary(
        string="Own New Investment Depreciation",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    own_old_asset_dep = fields.Monetary(
        string="Own Old Asset Depreciation",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_new_investment_dep_branch = fields.Monetary(
        string="Allocated New Investment Depreciation (Branch)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_new_investment_dep_center = fields.Monetary(
        string="Allocated New Investment Depreciation (Center)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_old_asset_dep_branch = fields.Monetary(
        string="Allocated Old Asset Depreciation (Branch)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_old_asset_dep_center = fields.Monetary(
        string="Allocated Old Asset Depreciation (Center)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_financial_investment_branch = fields.Monetary(
        string="Allocated Financial Investment (Branch)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="Ancestor branch's financial investment allocated by "
        "pct_up, at full nominal value (never depreciated).",
    )
    allocated_financial_investment_center = fields.Monetary(
        string="Allocated Financial Investment (Center)",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="Ancestor center's financial investment allocated by "
        "pct_up, at full nominal value (never depreciated).",
    )
    total_up_dep = fields.Monetary(
        string="Total UP Depreciation",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="Own new/old asset depreciation plus depreciation "
        "allocated from branch and center.",
    )
    total_up_cost_with_dep = fields.Monetary(
        string="Total UP Cost With Depreciation",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_up_cost + total_up_dep + allocated financial "
        "investments from branch and center. This is the UP tariff "
        "divisor's numerator.",
    )
    auto_up_rate = fields.Monetary(
        string="Auto UP Rate",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_up_cost_with_dep / new_student_count (guarded: "
        "0 students is treated as 1).",
    )
    final_up_rate = fields.Monetary(
        string="Final UP Rate",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="override_up_rate as-is when Override UP Rate is "
        "enabled, otherwise auto_up_rate.",
    )
    total_up_revenue = fields.Monetary(
        string="Total UP Revenue",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="final_up_rate * new_student_count.",
    )
    auto_up_revenue = fields.Monetary(
        string="Auto UP Revenue",
        compute="_compute_up_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="auto_up_rate * new_student_count.",
    )
    total_own_us_cost = fields.Monetary(
        string="Own US Cost",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of (foundation + bos) of this unit's own expense "
        "lines that are operational, not a UP component, and not "
        "direct income.",
    )
    allocated_us_branch = fields.Monetary(
        string="Allocated US Cost (Branch)",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    allocated_us_center = fields.Monetary(
        string="Allocated US Cost (Center)",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_us_cost = fields.Monetary(
        string="Total US Cost",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_own_us_cost + allocated_us_branch + "
        "allocated_us_center. Never includes depreciation.",
    )
    auto_us_rate = fields.Monetary(
        string="Auto US Rate",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_us_cost / (total_student_count * 12), guarded: "
        "0 students is treated as 1.",
    )
    final_us_rate = fields.Monetary(
        string="Final US Rate",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="override_us_rate as-is when Override US Rate is "
        "enabled, otherwise auto_us_rate.",
    )
    total_us_revenue = fields.Monetary(
        string="Total US Revenue",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="final_us_rate * total_student_count * 12.",
    )
    auto_us_revenue = fields.Monetary(
        string="Auto US Revenue",
        compute="_compute_us_simulation",
        compute_sudo=True,
        currency_field="currency_id",
        help="auto_us_rate * total_student_count * 12.",
    )

    def _get_pct_from_ancestor(self, ancestor_budget):
        self.ensure_one()
        allocation = self.env["school_budget_contribution_allocation"].search(
            [
                ("parent_budget_id", "=", ancestor_budget.id),
                ("child_budget_id", "=", self.id),
            ],
            limit=1,
        )
        if not allocation:
            return 0.0, 0.0
        return allocation.pct_up, allocation.pct_us

    def _get_allocated_components_from_ancestor(self, ancestor_budget):
        self.ensure_one()
        pct_up, pct_us = self._get_pct_from_ancestor(ancestor_budget)
        allocated_up = 0.0
        allocated_us = 0.0
        for pea in ancestor_budget.parent_expense_allocation_ids.filtered("active"):
            lines = ancestor_budget.expense_line_ids.filtered(
                lambda line, cat=pea.expense_category_id: line.expense_category_id
                == cat
            )
            parent_total = sum(lines.mapped(lambda line: line.foundation + line.bos))
            if pea.affects_up:
                allocated_up += pct_up * parent_total
            else:
                allocated_us += pct_us * parent_total
        return allocated_up, allocated_us

    def _get_allocated_dep_from_ancestor(self, ancestor_budget):
        self.ensure_one()
        pct_up, _pct_us = self._get_pct_from_ancestor(ancestor_budget)
        dep_new = pct_up * ancestor_budget.total_new_investment_dep
        dep_old = pct_up * ancestor_budget.total_old_asset_dep
        fin_inv = pct_up * ancestor_budget.total_financial_investment
        return dep_new, dep_old, fin_inv

    def _get_parent_allocated_components(self, include_parent_allocation=None):
        self.ensure_one()
        if include_parent_allocation is None:
            include_parent_allocation = self.include_parent_allocation
        result = {
            "up_branch": 0.0,
            "up_center": 0.0,
            "us_branch": 0.0,
            "us_center": 0.0,
            "dep_new_branch": 0.0,
            "dep_new_center": 0.0,
            "dep_old_branch": 0.0,
            "dep_old_center": 0.0,
            "fin_inv_branch": 0.0,
            "fin_inv_center": 0.0,
        }
        if not include_parent_allocation:
            return result
        for ancestor in self._get_ancestor_budgets():
            level = "center" if ancestor.org_type == "center" else "branch"
            allocated_up, allocated_us = self._get_allocated_components_from_ancestor(
                ancestor
            )
            dep_new, dep_old, fin_inv = self._get_allocated_dep_from_ancestor(ancestor)
            result["up_%s" % level] += allocated_up
            result["us_%s" % level] += allocated_us
            result["dep_new_%s" % level] += dep_new
            result["dep_old_%s" % level] += dep_old
            result["fin_inv_%s" % level] += fin_inv
        return result

    def _compute_up_us_values(self, include_parent_allocation):
        """Pure calculation of every UP/US simulation figure for a
        single record, honoring an explicit include_parent_allocation
        flag instead of reading the stored field. This is the single
        source of truth for the UP/US formulas: both the stored
        compute fields below (using self.include_parent_allocation)
        and the comparative summary (BL-0118, using a temporary
        False) call this same method so the two can never drift
        apart.
        """
        self.ensure_one()
        zero_values = {
            "total_own_up_cost": 0.0,
            "allocated_up_branch": 0.0,
            "allocated_up_center": 0.0,
            "total_up_cost": 0.0,
            "own_new_investment_dep": 0.0,
            "own_old_asset_dep": 0.0,
            "allocated_new_investment_dep_branch": 0.0,
            "allocated_new_investment_dep_center": 0.0,
            "allocated_old_asset_dep_branch": 0.0,
            "allocated_old_asset_dep_center": 0.0,
            "allocated_financial_investment_branch": 0.0,
            "allocated_financial_investment_center": 0.0,
            "total_up_dep": 0.0,
            "total_up_cost_with_dep": 0.0,
            "auto_up_rate": 0.0,
            "final_up_rate": 0.0,
            "total_up_revenue": 0.0,
            "auto_up_revenue": 0.0,
            "total_own_us_cost": 0.0,
            "allocated_us_branch": 0.0,
            "allocated_us_center": 0.0,
            "total_us_cost": 0.0,
            "auto_us_rate": 0.0,
            "final_us_rate": 0.0,
            "total_us_revenue": 0.0,
            "auto_us_revenue": 0.0,
        }
        if self.org_type != "unit":
            return zero_values
        allocated = self._get_parent_allocated_components(include_parent_allocation)
        total_own_up_cost = sum(
            self.expense_line_ids.filtered("is_up_component").mapped(
                lambda line: line.foundation + line.bos
            )
        )
        total_up_cost = (
            total_own_up_cost + allocated["up_branch"] + allocated["up_center"]
        )
        own_new_investment_dep = sum(self.investment_ids.mapped("dep_current_year"))
        own_old_asset_dep = sum(self.old_asset_ids.mapped("dep_current_year"))
        total_up_dep = (
            own_new_investment_dep
            + own_old_asset_dep
            + allocated["dep_new_branch"]
            + allocated["dep_new_center"]
            + allocated["dep_old_branch"]
            + allocated["dep_old_center"]
        )
        total_up_cost_with_dep = (
            total_up_cost
            + total_up_dep
            + allocated["fin_inv_branch"]
            + allocated["fin_inv_center"]
        )
        new_student_count = self.new_student_count or 1
        auto_up_rate = total_up_cost_with_dep / new_student_count
        final_up_rate = (
            self.override_up_rate if self.is_up_rate_overridden else auto_up_rate
        )
        us_lines = self.expense_line_ids.filtered(
            lambda line: line.is_operational
            and not line.is_up_component
            and not line.is_direct_income
        )
        total_own_us_cost = sum(
            us_lines.mapped(lambda line: line.foundation + line.bos)
        )
        total_us_cost = (
            total_own_us_cost + allocated["us_branch"] + allocated["us_center"]
        )
        total_students = self.total_student_count or 1
        auto_us_rate = total_us_cost / (total_students * 12)
        final_us_rate = (
            self.override_us_rate if self.is_us_rate_overridden else auto_us_rate
        )
        return {
            "total_own_up_cost": total_own_up_cost,
            "allocated_up_branch": allocated["up_branch"],
            "allocated_up_center": allocated["up_center"],
            "total_up_cost": total_up_cost,
            "own_new_investment_dep": own_new_investment_dep,
            "own_old_asset_dep": own_old_asset_dep,
            "allocated_new_investment_dep_branch": allocated["dep_new_branch"],
            "allocated_new_investment_dep_center": allocated["dep_new_center"],
            "allocated_old_asset_dep_branch": allocated["dep_old_branch"],
            "allocated_old_asset_dep_center": allocated["dep_old_center"],
            "allocated_financial_investment_branch": allocated["fin_inv_branch"],
            "allocated_financial_investment_center": allocated["fin_inv_center"],
            "total_up_dep": total_up_dep,
            "total_up_cost_with_dep": total_up_cost_with_dep,
            "auto_up_rate": auto_up_rate,
            "final_up_rate": final_up_rate,
            "total_up_revenue": final_up_rate * new_student_count,
            "auto_up_revenue": auto_up_rate * new_student_count,
            "total_own_us_cost": total_own_us_cost,
            "allocated_us_branch": allocated["us_branch"],
            "allocated_us_center": allocated["us_center"],
            "total_us_cost": total_us_cost,
            "auto_us_rate": auto_us_rate,
            "final_us_rate": final_us_rate,
            "total_us_revenue": final_us_rate * total_students * 12,
            "auto_us_revenue": auto_us_rate * total_students * 12,
        }

    @api.depends(
        "org_type",
        "include_parent_allocation",
        "expense_line_ids.foundation",
        "expense_line_ids.bos",
        "expense_line_ids.is_up_component",
        "investment_ids.dep_current_year",
        "old_asset_ids.dep_current_year",
        "new_student_count",
        "is_up_rate_overridden",
        "override_up_rate",
    )
    def _compute_up_simulation(self):
        """Fill the UP (Uang Pangkal) simulation result fields.

        Delegates the actual math to
        ``_compute_up_us_values(include_parent_allocation)`` and
        copies the UP-specific keys onto this record.
        """
        up_fields = [
            "total_own_up_cost",
            "allocated_up_branch",
            "allocated_up_center",
            "total_up_cost",
            "own_new_investment_dep",
            "own_old_asset_dep",
            "allocated_new_investment_dep_branch",
            "allocated_new_investment_dep_center",
            "allocated_old_asset_dep_branch",
            "allocated_old_asset_dep_center",
            "allocated_financial_investment_branch",
            "allocated_financial_investment_center",
            "total_up_dep",
            "total_up_cost_with_dep",
            "auto_up_rate",
            "final_up_rate",
            "total_up_revenue",
            "auto_up_revenue",
        ]
        for record in self:
            values = record._compute_up_us_values(record.include_parent_allocation)
            for field_name in up_fields:
                record[field_name] = values[field_name]

    @api.depends(
        "org_type",
        "include_parent_allocation",
        "expense_line_ids.foundation",
        "expense_line_ids.bos",
        "expense_line_ids.is_operational",
        "expense_line_ids.is_up_component",
        "expense_line_ids.is_direct_income",
        "total_student_count",
        "is_us_rate_overridden",
        "override_us_rate",
    )
    def _compute_us_simulation(self):
        """Fill the US (Uang Sekolah) simulation result fields.

        Delegates the actual math to
        ``_compute_up_us_values(include_parent_allocation)`` and
        copies the US-specific keys onto this record.
        """
        us_fields = [
            "total_own_us_cost",
            "allocated_us_branch",
            "allocated_us_center",
            "total_us_cost",
            "auto_us_rate",
            "final_us_rate",
            "total_us_revenue",
            "auto_us_revenue",
        ]
        for record in self:
            values = record._compute_up_us_values(record.include_parent_allocation)
            for field_name in us_fields:
                record[field_name] = values[field_name]

    # ------------------------------------------------------------
    # Income / expense simulation results (BL-0117)
    # ------------------------------------------------------------

    income_result_ids = fields.One2many(
        string="Income Results",
        comodel_name="school_budget_income_result",
        inverse_name="budget_id",
        readonly=True,
        help="Generated income lines, written by action_simulate().",
    )
    expense_result_ids = fields.One2many(
        string="Expense Results",
        comodel_name="school_budget_expense_result",
        inverse_name="budget_id",
        readonly=True,
        help="Generated expense lines, written by action_simulate().",
    )
    total_income_result = fields.Monetary(
        string="Total Income Result",
        compute="_compute_total_income_result",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_income_result_auto = fields.Monetary(
        string="Total Income Result (Auto)",
        compute="_compute_total_income_result",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_expense_operational = fields.Monetary(
        string="Total Operational Expense Result",
        compute="_compute_total_expense_result",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_expense_non_operational = fields.Monetary(
        string="Total Non Operational Expense Result",
        compute="_compute_total_expense_result",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_expense_result = fields.Monetary(
        string="Total Expense Result",
        compute="_compute_total_expense_result",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )

    @api.depends("income_result_ids.amount", "income_result_ids.auto_amount")
    def _compute_total_income_result(self):
        """Sum income_result_ids into the income result totals.

        Fills ``total_income_result`` and
        ``total_income_result_auto``.
        """
        for record in self:
            record.total_income_result = sum(record.income_result_ids.mapped("amount"))
            record.total_income_result_auto = sum(
                record.income_result_ids.mapped("auto_amount")
            )

    @api.depends("expense_result_ids.amount_total", "expense_result_ids.expense_group")
    def _compute_total_expense_result(self):
        """Split expense_result_ids into operational/non-operational.

        Fills ``total_expense_operational``,
        ``total_expense_non_operational``, and
        ``total_expense_result``.
        """
        for record in self:
            operational = record.expense_result_ids.filtered(
                lambda r: r.expense_group == "operational"
            )
            non_operational = record.expense_result_ids.filtered(
                lambda r: r.expense_group == "non_operational"
            )
            record.total_expense_operational = sum(operational.mapped("amount_total"))
            record.total_expense_non_operational = sum(
                non_operational.mapped("amount_total")
            )
            record.total_expense_result = (
                record.total_expense_operational + record.total_expense_non_operational
            )

    def _get_unit_setoran_to_ancestor(self, ancestor_budget):
        self.ensure_one()
        allocated_up, allocated_us = self._get_allocated_components_from_ancestor(
            ancestor_budget
        )
        dep_new, dep_old, fin_inv = self._get_allocated_dep_from_ancestor(
            ancestor_budget
        )
        setoran_up = allocated_up + dep_new + dep_old + fin_inv
        setoran_us = allocated_us
        return setoran_up, setoran_us

    def action_simulate(self):
        for record in self.sudo():
            record._simulate()

    def _simulate(self):
        self.ensure_one()
        self.income_result_ids.unlink()
        self.expense_result_ids.unlink()
        self.allocation_result_ids.unlink()
        self.comparative_result_ids.unlink()
        self._generate_income_result()
        self._generate_expense_result()
        self._generate_allocation_result()
        self._generate_comparative_result()

    def _generate_income_result(self):
        self.ensure_one()
        result_model = self.env["school_budget_income_result"]
        vals_list = []
        if self.org_type == "unit":
            vals_list += self._get_income_result_simulated_up_vals()
            vals_list += self._get_income_result_simulated_us_vals()
            vals_list += self._get_income_result_direct_income_vals()
        else:
            vals_list += self._get_income_result_contribution_vals()
        vals_list += self._get_income_result_bos_vals()
        vals_list += self._get_income_result_manual_vals()
        vals_list += self._get_income_result_subsidy_vals()
        if vals_list:
            result_model.create(vals_list)

    def _get_income_result_simulated_up_vals(self):
        self.ensure_one()
        categories = self.env["school_budget_income_category"].search(
            [("calc_method", "=", "simulated_up")]
        )
        return [
            {
                "budget_id": self.id,
                "income_category_id": category.id,
                "code": category.code,
                "label": category.name,
                "amount": self.total_up_revenue,
                "auto_amount": self.auto_up_revenue,
                "source": "simulated_up",
            }
            for category in categories
        ]

    def _get_income_result_simulated_us_vals(self):
        self.ensure_one()
        categories = self.env["school_budget_income_category"].search(
            [("calc_method", "=", "simulated_us")]
        )
        return [
            {
                "budget_id": self.id,
                "income_category_id": category.id,
                "code": category.code,
                "label": category.name,
                "amount": self.total_us_revenue,
                "auto_amount": self.auto_us_revenue,
                "source": "simulated_us",
            }
            for category in categories
        ]

    def _get_income_result_direct_income_vals(self):
        self.ensure_one()
        vals_list = []
        direct_categories = self.expense_line_ids.mapped(
            "expense_category_id"
        ).filtered("is_direct_income")
        for category in direct_categories:
            lines = self.expense_line_ids.filtered(
                lambda line, cat=category: line.expense_category_id == cat
            )
            auto_amount = sum(lines.mapped("foundation"))
            target = category.maps_to_income_category_id
            if target.calc_method == "grade_based":
                grade_total = sum(lines.mapped("grade_allocation_ids").mapped("amount"))
                if grade_total:
                    auto_amount = grade_total
            override = self.direct_income_override_ids.filtered(
                lambda o, cat=category: o.expense_category_id == cat
            )
            final_amount = override.override_amount if override else auto_amount
            vals_list.append(
                {
                    "budget_id": self.id,
                    "income_category_id": target.id,
                    "code": target.code,
                    "label": target.name,
                    "amount": final_amount,
                    "auto_amount": auto_amount,
                    "source": "direct_income",
                }
            )
        return vals_list

    def _get_income_result_bos_vals(self):
        self.ensure_one()
        categories = self.env["school_budget_income_category"].search(
            [("calc_method", "=", "sum_from_bos")]
        )
        vals_list = []
        for category in categories:
            amount = sum(self.expense_line_ids.mapped("bos")) + sum(
                self.investment_ids.mapped("bos")
            )
            vals_list.append(
                {
                    "budget_id": self.id,
                    "income_category_id": category.id,
                    "code": category.code,
                    "label": category.name,
                    "amount": amount,
                    "auto_amount": amount,
                    "source": "bos",
                }
            )
        return vals_list

    def _get_income_result_manual_vals(self):
        self.ensure_one()
        categories = self.income_line_ids.mapped("income_category_id")
        vals_list = []
        for category in categories:
            lines = self.income_line_ids.filtered(
                lambda line, cat=category: line.income_category_id == cat
            )
            amount = sum(lines.mapped("amount"))
            vals_list.append(
                {
                    "budget_id": self.id,
                    "income_category_id": category.id,
                    "code": category.code,
                    "label": category.name,
                    "amount": amount,
                    "auto_amount": amount,
                    "source": "manual",
                }
            )
        return vals_list

    def _get_income_result_contribution_vals(self):
        self.ensure_one()
        vals_list = []
        for allocation in self.contribution_allocation_ids:
            child = allocation.child_budget_id
            if not child.include_parent_allocation:
                continue
            setoran_up, setoran_us = child._get_unit_setoran_to_ancestor(self)
            vals_list.append(
                {
                    "budget_id": self.id,
                    "code": child.name,
                    "label": "Contribution UP from %s" % (child.school_id.name,),
                    "amount": setoran_up,
                    "auto_amount": setoran_up,
                    "source": "contribution_up",
                }
            )
            vals_list.append(
                {
                    "budget_id": self.id,
                    "code": child.name,
                    "label": "Contribution US from %s" % (child.school_id.name,),
                    "amount": setoran_us,
                    "auto_amount": setoran_us,
                    "source": "contribution_us",
                }
            )
        return vals_list

    def _get_income_result_subsidy_vals(self):
        self.ensure_one()
        subsidies = self.received_subsidy_ids.filtered("active")
        categories = subsidies.mapped("income_category_id")
        vals_list = []
        for category in categories:
            lines = subsidies.filtered(
                lambda s, cat=category: s.income_category_id == cat
            )
            amount = sum(lines.mapped("amount"))
            vals_list.append(
                {
                    "budget_id": self.id,
                    "income_category_id": category.id,
                    "code": category.code,
                    "label": category.name,
                    "amount": amount,
                    "auto_amount": amount,
                    "source": "subsidy",
                }
            )
        return vals_list

    def _generate_expense_result(self):
        self.ensure_one()
        result_model = self.env["school_budget_expense_result"]
        vals_list = []
        vals_list += self._get_expense_result_own_vals()
        vals_list += self._get_expense_result_subsidy_given_vals()
        if self.org_type == "unit" and self.include_parent_allocation:
            vals_list += self._get_expense_result_allocated_vals()
        if vals_list:
            result_model.create(vals_list)

    def _get_expense_result_own_vals(self):
        self.ensure_one()
        categories = self.expense_line_ids.mapped("expense_category_id")
        vals_list = []
        for category in categories:
            lines = self.expense_line_ids.filtered(
                lambda line, cat=category: line.expense_category_id == cat
            )
            amount_foundation = sum(lines.mapped("foundation"))
            amount_bos = sum(lines.mapped("bos"))
            vals_list.append(
                {
                    "budget_id": self.id,
                    "expense_category_id": category.id,
                    "code": category.code,
                    "label": category.name,
                    "amount_foundation": amount_foundation,
                    "amount_bos": amount_bos,
                    "amount_total": amount_foundation + amount_bos,
                    "expense_group": (
                        "operational" if category.is_operational else "non_operational"
                    ),
                    "source": "own",
                }
            )
        return vals_list

    def _get_expense_result_subsidy_given_vals(self):
        self.ensure_one()
        subsidies = self.subsidy_ids.filtered("active")
        categories = subsidies.mapped("expense_category_id")
        vals_list = []
        for category in categories:
            lines = subsidies.filtered(
                lambda s, cat=category: s.expense_category_id == cat
            )
            amount = sum(lines.mapped("amount"))
            vals_list.append(
                {
                    "budget_id": self.id,
                    "expense_category_id": category.id,
                    "code": category.code,
                    "label": category.name,
                    "amount_foundation": amount,
                    "amount_bos": 0.0,
                    "amount_total": amount,
                    "expense_group": (
                        "operational" if category.is_operational else "non_operational"
                    ),
                    "source": "subsidy_given",
                }
            )
        return vals_list

    def _get_expense_result_allocated_vals(self):
        self.ensure_one()
        components = [
            (
                "allocated_up",
                "Allocated UP Cost",
                self.allocated_up_branch + self.allocated_up_center,
            ),
            (
                "allocated_us",
                "Allocated US Cost",
                self.allocated_us_branch + self.allocated_us_center,
            ),
            (
                "allocated_dep_new",
                "Allocated New Investment Depreciation",
                self.allocated_new_investment_dep_branch
                + self.allocated_new_investment_dep_center,
            ),
            (
                "allocated_dep_old",
                "Allocated Old Asset Depreciation",
                self.allocated_old_asset_dep_branch
                + self.allocated_old_asset_dep_center,
            ),
            (
                "allocated_financial_investment",
                "Allocated Financial Investment",
                self.allocated_financial_investment_branch
                + self.allocated_financial_investment_center,
            ),
        ]
        vals_list = []
        for source, label, amount in components:
            if not amount:
                continue
            vals_list.append(
                {
                    "budget_id": self.id,
                    "label": label,
                    "amount_foundation": amount,
                    "amount_bos": 0.0,
                    "amount_total": amount,
                    "expense_group": "operational",
                    "source": source,
                }
            )
        return vals_list

    # ------------------------------------------------------------
    # Cash vs accrual summary, allocation, and comparative results
    # (BL-0118)
    # ------------------------------------------------------------

    total_cash_revenue = fields.Monetary(
        string="Total Cash Revenue",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="Same as Total Income Result (final amounts).",
    )
    total_cash_revenue_auto = fields.Monetary(
        string="Total Cash Revenue (Auto)",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="Same as Total Income Result (Auto), ignoring tariff " "overrides.",
    )
    total_cash_expense = fields.Monetary(
        string="Total Cash Expense",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="Same as Total Expense Result.",
    )
    cash_surplus_deficit = fields.Monetary(
        string="Cash Surplus/Deficit",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_cash_revenue - total_cash_expense - total_investment "
        "(cash accounting expenses the full investment purchase).",
    )
    cash_surplus_deficit_auto = fields.Monetary(
        string="Cash Surplus/Deficit (Auto)",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
    )
    opening_cash_balance = fields.Monetary(
        string="Opening Cash Balance",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="Same as cash_balance, exposed under the Summary page.",
    )
    ending_cash_balance = fields.Monetary(
        string="Ending Cash Balance",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="opening_cash_balance + cash_surplus_deficit.",
    )
    ending_cash_balance_auto = fields.Monetary(
        string="Ending Cash Balance (Auto)",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_accrual_expense = fields.Monetary(
        string="Total Accrual Expense",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="total_cash_expense + total_depreciation (own assets "
        "only; accrual accounting expenses depreciation instead of "
        "the investment purchase).",
    )
    accrual_surplus_deficit = fields.Monetary(
        string="Accrual Surplus/Deficit",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
    )
    accrual_surplus_deficit_auto = fields.Monetary(
        string="Accrual Surplus/Deficit (Auto)",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_accrual_revenue = fields.Monetary(
        string="Total Accrual Revenue",
        compute="_compute_cash_summary",
        compute_sudo=True,
        currency_field="currency_id",
        help="Identical to total_cash_revenue; there is no revenue "
        "side difference between cash and accrual.",
    )

    @api.depends(
        "income_result_ids.amount",
        "income_result_ids.auto_amount",
        "expense_result_ids.amount_total",
        "expense_result_ids.expense_group",
        "total_investment",
        "total_depreciation",
        "cash_balance",
    )
    def _compute_cash_summary(self):
        """Derive the cash and accrual budget summary totals.

        Combines income/expense simulation results, investments,
        depreciation, and the opening cash balance into the
        cash/accrual revenue, expense, and surplus/deficit fields
        shown on the Summary tab.
        """
        for record in self:
            total_cash_revenue = record.total_income_result
            total_cash_revenue_auto = record.total_income_result_auto
            total_cash_expense = record.total_expense_result
            total_investments = record.total_investment
            cash_surplus_deficit = (
                total_cash_revenue - total_cash_expense - total_investments
            )
            cash_surplus_deficit_auto = (
                total_cash_revenue_auto - total_cash_expense - total_investments
            )
            opening_cash_balance = record.cash_balance
            total_accrual_expense = total_cash_expense + record.total_depreciation
            record.total_cash_revenue = total_cash_revenue
            record.total_cash_revenue_auto = total_cash_revenue_auto
            record.total_cash_expense = total_cash_expense
            record.cash_surplus_deficit = cash_surplus_deficit
            record.cash_surplus_deficit_auto = cash_surplus_deficit_auto
            record.opening_cash_balance = opening_cash_balance
            record.ending_cash_balance = opening_cash_balance + cash_surplus_deficit
            record.ending_cash_balance_auto = (
                opening_cash_balance + cash_surplus_deficit_auto
            )
            record.total_accrual_expense = total_accrual_expense
            record.accrual_surplus_deficit = total_cash_revenue - total_accrual_expense
            record.accrual_surplus_deficit_auto = (
                total_cash_revenue_auto - total_accrual_expense
            )
            record.total_accrual_revenue = total_cash_revenue

    total_allocatable_base_up = fields.Monetary(
        string="Total Allocatable Base (UP)",
        compute="_compute_allocatable_base",
        compute_sudo=True,
        currency_field="currency_id",
        help="100% base before splitting among contributors: sum of "
        "(foundation+bos) of expense lines under affects_up "
        "categories, plus own new/old asset depreciation and "
        "financial investment.",
    )
    total_allocatable_base_us = fields.Monetary(
        string="Total Allocatable Base (US)",
        compute="_compute_allocatable_base",
        compute_sudo=True,
        currency_field="currency_id",
        help="100% base before splitting among contributors: sum of "
        "(foundation+bos) of expense lines under non-affects_up "
        "categories.",
    )

    @api.depends(
        "parent_expense_allocation_ids.affects_up",
        "parent_expense_allocation_ids.active",
        "parent_expense_allocation_ids.expense_category_id",
        "expense_line_ids.foundation",
        "expense_line_ids.bos",
        "investment_ids.dep_current_year",
        "old_asset_ids.dep_current_year",
        "financial_investment_ids.amount",
    )
    def _compute_allocatable_base(self):
        """Compute the 100% UP/US base before splitting to children.

        Fills ``total_allocatable_base_up`` (own expense lines under
        ``affects_up`` categories, plus depreciation and financial
        investment) and ``total_allocatable_base_us`` (own expense
        lines under non-``affects_up`` categories).
        """
        for record in self:
            base_up = 0.0
            base_us = 0.0
            for pea in record.parent_expense_allocation_ids.filtered("active"):
                lines = record.expense_line_ids.filtered(
                    lambda line, cat=pea.expense_category_id: line.expense_category_id
                    == cat
                )
                amount = sum(lines.mapped(lambda line: line.foundation + line.bos))
                if pea.affects_up:
                    base_up += amount
                else:
                    base_us += amount
            base_up += sum(record.investment_ids.mapped("dep_current_year"))
            base_up += sum(record.old_asset_ids.mapped("dep_current_year"))
            base_up += sum(record.financial_investment_ids.mapped("amount"))
            record.total_allocatable_base_up = base_up
            record.total_allocatable_base_us = base_us

    allocation_result_ids = fields.One2many(
        string="Allocation Results",
        comodel_name="school_budget_allocation_result",
        inverse_name="budget_id",
        readonly=True,
        help="Generated per-contributor allocation figures, written "
        "by action_simulate(). Only populated for branch/center "
        "budgets.",
    )
    comparative_result_ids = fields.One2many(
        string="Comparative Results",
        comodel_name="school_budget_comparative_result",
        inverse_name="budget_id",
        readonly=True,
        help="Generated self-vs-descendant-units comparison, written "
        "by action_simulate(). Only populated for branch/center "
        "budgets.",
    )

    def _generate_allocation_result(self):
        self.ensure_one()
        if self.org_type not in ("branch", "center"):
            return
        result_model = self.env["school_budget_allocation_result"]
        vals_list = []
        for allocation in self.contribution_allocation_ids:
            child = allocation.child_budget_id
            setoran_up, setoran_us = child._get_unit_setoran_to_ancestor(self)
            vals_list.append(
                {
                    "budget_id": self.id,
                    "child_budget_id": child.id,
                    "pct_up": allocation.pct_up,
                    "pct_us": allocation.pct_us,
                    "contribution_up": setoran_up,
                    "contribution_us": setoran_us,
                }
            )
        if vals_list:
            result_model.create(vals_list)

    def _get_comparative_targets(self):
        self.ensure_one()
        domain = [
            ("org_type", "=", "unit"),
            ("academic_year_id", "=", self.academic_year_id.id),
            ("company_id", "=", self.company_id.id),
            ("state", "!=", "cancel"),
        ]
        if self.org_type == "branch":
            domain.append(("branch_id", "=", self.branch_id.id))
        return self + self.search(domain)

    def _generate_comparative_result(self):
        self.ensure_one()
        if self.org_type not in ("branch", "center"):
            return
        result_model = self.env["school_budget_comparative_result"]
        vals_list = []
        for target in self._get_comparative_targets():
            revenue, expense = target._get_simulation_totals(True)
            revenue_no_alloc, expense_no_alloc = target._get_simulation_totals(False)
            dep = target.total_depreciation
            investment = target.total_investment
            vals_list.append(
                {
                    "budget_id": self.id,
                    "target_budget_id": target.id,
                    "revenue": revenue,
                    "expense": expense,
                    "cash_surplus": revenue - expense - investment,
                    "accrual_surplus": revenue - (expense + dep),
                    "revenue_no_alloc": revenue_no_alloc,
                    "expense_no_alloc": expense_no_alloc,
                    "cash_surplus_no_alloc": (
                        revenue_no_alloc - expense_no_alloc - investment
                    ),
                    "accrual_surplus_no_alloc": (
                        revenue_no_alloc - (expense_no_alloc + dep)
                    ),
                }
            )
        if vals_list:
            result_model.create(vals_list)

    def _get_simulation_totals(self, include_parent_allocation):
        """Compute (revenue, expense) totals for self as if
        include_parent_allocation were the given value, without
        persisting any rows or mutating the document. Reuses the
        same vals-generating helpers as action_simulate() (BL-0117)
        and the same pure UP/US calculation (BL-0116) so the
        comparative summary can never drift from the real
        simulation.
        """
        self.ensure_one()
        revenue = 0.0
        if self.org_type == "unit":
            up_us = self._compute_up_us_values(include_parent_allocation)
            if self.env["school_budget_income_category"].search_count(
                [("calc_method", "=", "simulated_up")]
            ):
                revenue += up_us["total_up_revenue"]
            if self.env["school_budget_income_category"].search_count(
                [("calc_method", "=", "simulated_us")]
            ):
                revenue += up_us["total_us_revenue"]
            revenue += sum(
                vals["amount"] for vals in self._get_income_result_direct_income_vals()
            )
        else:
            up_us = {}
            for allocation in self.contribution_allocation_ids:
                child = allocation.child_budget_id
                if not child.include_parent_allocation:
                    continue
                setoran_up, setoran_us = child._get_unit_setoran_to_ancestor(self)
                revenue += setoran_up + setoran_us
        revenue += sum(vals["amount"] for vals in self._get_income_result_bos_vals())
        revenue += sum(vals["amount"] for vals in self._get_income_result_manual_vals())
        revenue += sum(
            vals["amount"] for vals in self._get_income_result_subsidy_vals()
        )

        expense = sum(
            vals["amount_total"] for vals in self._get_expense_result_own_vals()
        )
        expense += sum(
            vals["amount_total"]
            for vals in self._get_expense_result_subsidy_given_vals()
        )
        if self.org_type == "unit" and include_parent_allocation:
            expense += up_us["allocated_up_branch"] + up_us["allocated_up_center"]
            expense += up_us["allocated_us_branch"] + up_us["allocated_us_center"]
            expense += (
                up_us["allocated_new_investment_dep_branch"]
                + up_us["allocated_new_investment_dep_center"]
            )
            expense += (
                up_us["allocated_old_asset_dep_branch"]
                + up_us["allocated_old_asset_dep_center"]
            )
            expense += (
                up_us["allocated_financial_investment_branch"]
                + up_us["allocated_financial_investment_center"]
            )
        return revenue, expense

    # ------------------------------------------------------------
    # Analytic account (BL-0120)
    # ------------------------------------------------------------

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        compute="_compute_analytic_account_id",
        store=True,
        compute_sudo=True,
        readonly=True,
        help=(
            "Analytic Account of this budget's organization, used to "
            "pull realization from posted journal items. Automatically "
            "derived: Unit uses the school's Analytic Account, Branch "
            "uses the branch's, Center uses the company's. This field "
            "is never a manual input, so two budgets can never point "
            "to the same Analytic Account."
        ),
    )

    @api.depends(
        "org_type",
        "school_id.analytic_account_id",
        "branch_id.analytic_account_id",
        "company_id.school_analytic_account_id",
    )
    def _compute_analytic_account_id(self):
        """Derive ``analytic_account_id`` from the organization.

        Unit uses the school's analytic account, branch uses the
        branch's, center uses the company's.
        """
        for record in self:
            if record.org_type == "unit":
                record.analytic_account_id = record.school_id.analytic_account_id
            elif record.org_type == "branch":
                record.analytic_account_id = record.branch_id.analytic_account_id
            else:
                record.analytic_account_id = (
                    record.company_id.school_analytic_account_id
                )

    @ssi_decorator.pre_confirm_check()
    def _10_check_analytic_account(self):
        """Block Confirm when the organization has no analytic account.

        Hooked as a ``pre_confirm_check`` via ``ssi_decorator``.

        :raises: :class:`~odoo.exceptions.UserError`
        """
        self.ensure_one()
        if not self.analytic_account_id:
            error_message = (
                _(
                    """
Context: Confirm school budget
Database ID: %s
Problem: The organization of this budget has no analytic account
Solution: Open the school/branch/company and create or select its
analytic account
"""
                )
                % (self.id,)
            )
            raise UserError(error_message)

    # ------------------------------------------------------------
    # Monthly realization from posted journal items (BL-0122)
    # ------------------------------------------------------------

    expense_realization_ids = fields.One2many(
        string="Expense Realization",
        comodel_name="school_budget_expense_realization",
        inverse_name="budget_id",
        readonly=True,
        help="Monthly realized expense per category, written by "
        "action_compute_realization().",
    )
    income_realization_ids = fields.One2many(
        string="Income Realization",
        comodel_name="school_budget_income_realization",
        inverse_name="budget_id",
        readonly=True,
        help="Monthly realized income per category, written by "
        "action_compute_realization().",
    )

    def _prepare_realization_domain(self, account_ids):
        """Single source of truth for what counts as 'realized':
        posted journal items on a mapped account, tagged with this
        budget's own organization Analytic Account (no roll-up from
        child organizations - that would double count what the
        simulation engine already consolidates via contribution),
        within the academic year's date range.
        """
        self.ensure_one()
        return [
            ("account_id", "in", account_ids),
            ("analytic_account_id", "=", self.analytic_account_id.id),
            ("date", ">=", self.academic_year_id.date_start),
            ("date", "<=", self.academic_year_id.date_end),
            ("parent_state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
        ]

    def _get_realization_month_date_range(self, month_index):
        """Return (start, end) dates for the calendar month that is
        month_index (1-12) relative to the academic year's start
        month, e.g. an academic year starting 2025-07-01 has month 1
        = July 2025, month 12 = June 2026.
        """
        self.ensure_one()
        start = self.academic_year_id.date_start
        total_months = start.month - 1 + (month_index - 1)
        year = start.year + total_months // 12
        month = total_months % 12 + 1
        range_start = datetime_date(year, month, 1)
        if month == 12:
            range_end = datetime_date(year + 1, 1, 1)
        else:
            range_end = datetime_date(year, month + 1, 1)
        return range_start, range_end

    def _compute_realization_data(self, categories, sign):
        """Return {(category, month_index): amount} for every
        (category, month) combination that has posted journal
        activity. Categories without account_id are skipped.

        Grouping is done with 12 explicit per-month read_group calls
        (one per month_index) instead of a single
        groupby=["date:month"] call, because read_group's date:month
        label (e.g. "July 2025") is locale-dependent and unsafe to
        parse back into a month number.
        """
        self.ensure_one()
        category_by_account = {
            category.account_id.id: category
            for category in categories
            if category.account_id
        }
        result = {}
        if not category_by_account:
            return result
        account_ids = list(category_by_account.keys())
        base_domain = self._prepare_realization_domain(account_ids)
        move_line_model = self.env["account.move.line"].sudo()
        for month_index in range(1, 13):
            range_start, range_end = self._get_realization_month_date_range(month_index)
            month_domain = base_domain + [
                ("date", ">=", range_start),
                ("date", "<", range_end),
            ]
            grouped = move_line_model.read_group(
                month_domain, ["balance:sum"], ["account_id"]
            )
            for group in grouped:
                category = category_by_account.get(group["account_id"][0])
                if category is None:
                    continue
                result[(category, month_index)] = (group["balance"] or 0.0) * sign
        return result

    def action_compute_realization(self):
        for record in self.sudo():
            record._compute_realization()

    def _compute_realization(self):
        """Rebuild the realization and budget-vs-actual rows.

        Deletes and regenerates ``expense_realization_ids``,
        ``income_realization_ids``, ``expense_comparison_ids``, and
        ``income_comparison_ids`` from posted journal items.
        """
        self.ensure_one()
        self.expense_realization_ids.unlink()
        self.income_realization_ids.unlink()
        self.expense_comparison_ids.unlink()
        self.income_comparison_ids.unlink()
        self._generate_expense_realization()
        self._generate_income_realization()
        self._generate_expense_comparison()
        self._generate_income_comparison()

    def _generate_expense_realization(self):
        self.ensure_one()
        categories = (
            self.env["school_budget_expense_category"]
            .sudo()
            .search([("account_id", "!=", False)])
        )
        data = self._compute_realization_data(categories, 1)
        vals_list = [
            {
                "budget_id": self.id,
                "expense_category_id": category.id,
                "month": month_index,
                "amount": amount,
            }
            for (category, month_index), amount in data.items()
        ]
        if vals_list:
            self.env["school_budget_expense_realization"].create(vals_list)

    def _generate_income_realization(self):
        self.ensure_one()
        categories = (
            self.env["school_budget_income_category"]
            .sudo()
            .search([("account_id", "!=", False)])
        )
        data = self._compute_realization_data(categories, -1)
        vals_list = [
            {
                "budget_id": self.id,
                "income_category_id": category.id,
                "month": month_index,
                "amount": amount,
            }
            for (category, month_index), amount in data.items()
        ]
        if vals_list:
            self.env["school_budget_income_realization"].create(vals_list)

    # ------------------------------------------------------------
    # Budget vs actual comparison and absorption rate (BL-0123)
    # ------------------------------------------------------------

    expense_comparison_ids = fields.One2many(
        string="Expense Comparison",
        comodel_name="school_budget_expense_comparison",
        inverse_name="budget_id",
        readonly=True,
        help="Budget-vs-actual comparison per expense category, "
        "written by action_compute_realization().",
    )
    income_comparison_ids = fields.One2many(
        string="Income Comparison",
        comodel_name="school_budget_income_comparison",
        inverse_name="budget_id",
        readonly=True,
        help="Budget-vs-actual comparison per income category, "
        "written by action_compute_realization().",
    )
    total_realized_expense = fields.Monetary(
        string="Total Realized Expense",
        compute="_compute_comparison_totals",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_realized_income = fields.Monetary(
        string="Total Realized Income",
        compute="_compute_comparison_totals",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    total_expense_variance = fields.Monetary(
        string="Total Expense Variance",
        compute="_compute_comparison_totals",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
    )
    expense_absorption_rate = fields.Float(
        string="Expense Absorption Rate (%)",
        compute="_compute_comparison_totals",
        store=True,
        compute_sudo=True,
        help="total_realized_expense / total budgeted expense * 100. "
        "0 when the budgeted total is 0 (guarded against division "
        "by zero).",
    )

    @api.depends(
        "expense_comparison_ids.realized_amount",
        "expense_comparison_ids.budget_amount",
        "income_comparison_ids.realized_amount",
    )
    def _compute_comparison_totals(self):
        """Sum budget-vs-actual comparison rows into totals.

        Fills ``total_realized_expense``, ``total_realized_income``,
        ``total_expense_variance``, and
        ``expense_absorption_rate``.
        """
        for record in self:
            total_realized_expense = sum(
                record.expense_comparison_ids.mapped("realized_amount")
            )
            total_budget_expense = sum(
                record.expense_comparison_ids.mapped("budget_amount")
            )
            record.total_realized_expense = total_realized_expense
            record.total_realized_income = sum(
                record.income_comparison_ids.mapped("realized_amount")
            )
            record.total_expense_variance = (
                total_budget_expense - total_realized_expense
            )
            record.expense_absorption_rate = (
                (total_realized_expense / total_budget_expense * 100)
                if total_budget_expense
                else 0.0
            )

    def _get_current_month_index(self):
        """Return the current month index (1-12) relative to the
        academic year's start month; 0 before date_start, 12 after
        date_end.
        """
        self.ensure_one()
        today = datetime_date.today()
        start = self.academic_year_id.date_start
        end = self.academic_year_id.date_end
        if not start or not end:
            return 0
        if today < start:
            return 0
        if today > end:
            return 12
        return (today.year - start.year) * 12 + (today.month - start.month) + 1

    def _generate_expense_comparison(self):
        self.ensure_one()
        current_month = self._get_current_month_index()
        categories = self.expense_line_ids.mapped(
            "expense_category_id"
        ) | self.expense_realization_ids.mapped("expense_category_id")
        vals_list = []
        for category in categories:
            lines = self.expense_line_ids.filtered(
                lambda line, cat=category: line.expense_category_id == cat
            )
            budget_amount = sum(lines.mapped(lambda line: line.foundation + line.bos))
            realizations = self.expense_realization_ids.filtered(
                lambda r, cat=category: r.expense_category_id == cat
            )
            realized_amount = sum(realizations.mapped("amount"))
            realized_amount_ytd = sum(
                realizations.filtered(lambda r, m=current_month: r.month <= m).mapped(
                    "amount"
                )
            )
            vals_list.append(
                {
                    "budget_id": self.id,
                    "expense_category_id": category.id,
                    "budget_amount": budget_amount,
                    "realized_amount": realized_amount,
                    "realized_amount_ytd": realized_amount_ytd,
                    "variance": budget_amount - realized_amount,
                    "absorption_rate": (
                        (realized_amount / budget_amount * 100)
                        if budget_amount
                        else 0.0
                    ),
                }
            )
        if vals_list:
            self.env["school_budget_expense_comparison"].create(vals_list)

    def _generate_income_comparison(self):
        self.ensure_one()
        current_month = self._get_current_month_index()
        categories = self.income_result_ids.mapped(
            "income_category_id"
        ) | self.income_realization_ids.mapped("income_category_id")
        vals_list = []
        for category in categories:
            results = self.income_result_ids.filtered(
                lambda r, cat=category: r.income_category_id == cat
            )
            budget_amount = sum(results.mapped("amount"))
            realizations = self.income_realization_ids.filtered(
                lambda r, cat=category: r.income_category_id == cat
            )
            realized_amount = sum(realizations.mapped("amount"))
            realized_amount_ytd = sum(
                realizations.filtered(lambda r, m=current_month: r.month <= m).mapped(
                    "amount"
                )
            )
            vals_list.append(
                {
                    "budget_id": self.id,
                    "income_category_id": category.id,
                    "budget_amount": budget_amount,
                    "realized_amount": realized_amount,
                    "realized_amount_ytd": realized_amount_ytd,
                    "variance": budget_amount - realized_amount,
                    "absorption_rate": (
                        (realized_amount / budget_amount * 100)
                        if budget_amount
                        else 0.0
                    ),
                }
            )
        if vals_list:
            self.env["school_budget_income_comparison"].create(vals_list)

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "done_ok",
            "cancel_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
