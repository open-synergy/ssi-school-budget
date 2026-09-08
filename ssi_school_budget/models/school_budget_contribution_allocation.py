# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolBudgetContributionAllocation(models.Model):
    """
    Registers a unit (child_budget_id) as a contributor to a
    branch/center budget (parent_budget_id), holding the student
    counts used as the proportion key and an optional override
    percentage. pct_up/pct_us implement the reference application's
    _ancestor_pcts algorithm: siblings with an override keep their
    exact value, the remaining percentage is split among
    non-overridden siblings proportional to their student count.
    The invariant is that pct_up (and pct_us) across all siblings of
    the same parent always sums to 1.0.
    """

    _name = "school_budget_contribution_allocation"
    _description = "School Budget Contribution Allocation"

    parent_budget_id = fields.Many2one(
        string="# Parent Budget",
        comodel_name="school_budget",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="The branch/center budget receiving the contribution.",
    )
    child_budget_id = fields.Many2one(
        string="Child Budget",
        comodel_name="school_budget",
        required=True,
        help="The unit budget contributing to the parent.",
    )
    total_student_count = fields.Integer(
        string="Total Student Count",
        default=0,
        help="Student count key used to compute pct_us. Deliberately "
        "separate from the unit's own assumption line total; not "
        "synced automatically.",
    )
    new_student_count = fields.Integer(
        string="New Student Count",
        default=0,
        help="New student count key used to compute pct_up. "
        "Deliberately separate from the unit's own assumption; not "
        "synced automatically.",
    )
    is_pct_up_overridden = fields.Boolean(
        string="Override UP Percentage",
        default=False,
        help="When enabled, Override UP Percentage is used as pct_up "
        "instead of the automatically computed proportion. Substitute "
        "for the reference application's 'None = automatic' "
        "semantics: an override of 0.0 is a valid value.",
    )
    override_pct_up = fields.Float(
        string="Override UP Percentage",
        default=0.0,
        help="Manually forced pct_up (0.0-1.0). Only used when "
        "'Override UP Percentage' is enabled.",
    )
    is_pct_us_overridden = fields.Boolean(
        string="Override US Percentage",
        default=False,
        help="When enabled, Override US Percentage is used as pct_us "
        "instead of the automatically computed proportion.",
    )
    override_pct_us = fields.Float(
        string="Override US Percentage",
        default=0.0,
        help="Manually forced pct_us (0.0-1.0). Only used when "
        "'Override US Percentage' is enabled.",
    )
    pct_up = fields.Float(
        string="UP Percentage",
        compute="_compute_pct",
        compute_sudo=True,
        help="Share of the parent's UP-allocatable cost pushed down "
        "to this child. Computed from all siblings under the same "
        "parent; not stored because it depends on sibling records.",
    )
    pct_us = fields.Float(
        string="US Percentage",
        compute="_compute_pct",
        compute_sudo=True,
        help="Share of the parent's US-allocatable cost pushed down "
        "to this child. Computed from all siblings under the same "
        "parent; not stored because it depends on sibling records.",
    )

    @api.constrains("parent_budget_id", "child_budget_id")
    def _check_unique_parent_child(self):
        """Reject a duplicate child budget under the same parent.

        Replaces the former ``_sql_constraints`` entry so the
        error is raised as ``ValidationError`` instead of a
        raw ``IntegrityError``.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_unique_parent_child_condition():
                error_message = (
                    _(
                        """
Context: Save school budget contribution allocation
Database ID: %s
Problem: Only one contribution allocation is allowed per child
budget under the same parent budget
Solution: Edit the existing allocation instead of creating a
duplicate
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_unique_parent_child_condition(self):
        """Return whether the unique key still holds.

        :return: ``True`` when no other record shares the
            same key
        """
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("parent_budget_id", "=", self.parent_budget_id.id),
            ("child_budget_id", "=", self.child_budget_id.id),
        ]
        return self.search_count(domain) == 0

    @api.depends(
        "parent_budget_id",
        "parent_budget_id.contribution_allocation_ids.new_student_count",
        "parent_budget_id.contribution_allocation_ids.total_student_count",
        "parent_budget_id.contribution_allocation_ids.is_pct_up_overridden",
        "parent_budget_id.contribution_allocation_ids.override_pct_up",
        "parent_budget_id.contribution_allocation_ids.is_pct_us_overridden",
        "parent_budget_id.contribution_allocation_ids.override_pct_us",
    )
    def _compute_pct(self):
        """Derive pct_up/pct_us from sibling contribution allocations.

        Delegates the split-remaining-by-count math to
        ``_compute_ancestor_pct`` for each of the UP and US sides.
        """
        for record in self:
            if not record.parent_budget_id:
                record.pct_up = 0.0
                record.pct_us = 0.0
                continue
            siblings = self.search(
                [("parent_budget_id", "=", record.parent_budget_id.id)]
            )
            record.pct_up = record._compute_ancestor_pct(
                siblings, "is_pct_up_overridden", "override_pct_up", "new_student_count"
            )
            record.pct_us = record._compute_ancestor_pct(
                siblings,
                "is_pct_us_overridden",
                "override_pct_us",
                "total_student_count",
            )

    def _compute_ancestor_pct(
        self, siblings, override_flag_field, override_value_field, count_field
    ):
        """Return this record's share of a parent's allocatable base.

        Siblings with the override flag keep their exact override
        value; the remaining percentage (1.0 minus the sum of
        overrides) is split among non-overridden siblings
        proportional to ``count_field``.

        :param siblings: all contribution allocations under the
            same ``parent_budget_id``
        :param override_flag_field: name of the boolean override
            flag field
        :param override_value_field: name of the override value
            field
        :param count_field: name of the student-count field used as
            the proportion key
        :return: the computed percentage (0.0-1.0) for this record
        """
        self.ensure_one()
        if self[override_flag_field]:
            return self[override_value_field]
        overridden = siblings.filtered(lambda s: s[override_flag_field])
        non_overridden = siblings - overridden
        sum_override = sum(overridden.mapped(override_value_field))
        remaining = max(0.0, 1.0 - sum_override)
        auto_total = sum(non_overridden.mapped(count_field)) or 1
        return remaining * (self[count_field] / auto_total)

    @api.constrains(
        "parent_budget_id",
        "child_budget_id",
        "override_pct_up",
        "override_pct_us",
    )
    def _check_contribution_allocation(self):
        """Reject an invalid parent/child pairing or override value.

        :raises: :class:`~odoo.exceptions.ValidationError`
        """
        for record in self.sudo():
            if not record._check_contribution_allocation_condition():
                error_message = (
                    _(
                        """
Context: Save school budget contribution allocation
Database ID: %s
Problem: Invalid parent/child organization type, parent equals
child, mismatched academic year, or override percentage out of
range (0.0-1.0)
Solution: Parent budget must be branch/center, child budget must be
a unit under the same academic year and different from the parent,
and override percentages must be between 0.0 and 1.0
"""
                    )
                    % (record.id,)
                )
                raise ValidationError(error_message)

    def _check_contribution_allocation_condition(self):
        """Return whether this allocation's org/year/pct are valid.

        :return: ``True`` when parent is branch/center, child is a
            unit different from the parent under the same academic
            year, and both override percentages are within
            0.0-1.0
        """
        self.ensure_one()
        if self.parent_budget_id.org_type not in ("branch", "center"):
            return False
        if self.child_budget_id.org_type != "unit":
            return False
        if self.parent_budget_id == self.child_budget_id:
            return False
        if (
            self.parent_budget_id.academic_year_id
            != self.child_budget_id.academic_year_id
        ):
            return False
        if not 0.0 <= self.override_pct_up <= 1.0:
            return False
        if not 0.0 <= self.override_pct_us <= 1.0:
            return False
        return True
