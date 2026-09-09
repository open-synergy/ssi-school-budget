# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. 14.0's HttpCase does not set up
# cls.env in setUpClass (see odoo-development-ui-test skill).
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolBudget(HttpSavepointCase):
    """Tour tests for the ``school_budget`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the schools, years, and budgets the tours act on.

        ``user_id`` is set explicitly on every fixture: ``cls.env``
        runs as SUPERUSER, and the ``school_budget_internal_user_rule``
        record rule would otherwise hide these fixtures from the
        tour's admin browser session.
        """
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")
        cls.grade_type = cls.env["school_grade_type"].create(
            {
                "name": "Grade Type Tour Budget",
                "code": "GTTB",
                "sequence": 10,
            }
        )

        # -- Create tour: only the school + academic year exist; the
        # tour itself builds the budget through the UI.
        cls.school_create = cls.env["school"].create(
            {
                "name": "School Tour Create",
                "code": "SCHTC",
                "grade_type_id": cls.grade_type.id,
            }
        )
        cls.academic_year_create = cls.env["school_academic_year"].create(
            {
                "name": "Year Tour Create",
                "code": "AYTC",
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )

        # -- Confirm tour: draft budget whose school already has an
        # analytic account (Confirm's Pre-Condition).
        cls.school_confirm = cls.env["school"].create(
            {
                "name": "School Tour Confirm",
                "code": "SCHTF",
                "grade_type_id": cls.grade_type.id,
            }
        )
        cls.school_confirm.action_create_analytic_account()
        cls.academic_year_confirm = cls.env["school_academic_year"].create(
            {
                "name": "Year Tour Confirm",
                "code": "AYTF",
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        cls.budget_confirm = cls.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": cls.school_confirm.id,
                "academic_year_id": cls.academic_year_confirm.id,
                "user_id": cls.admin.id,
            }
        )

        # -- Approve tour: budget already confirmed (Approve's
        # Pre-Condition is "Waiting for Approval"). confirm_ok is a
        # restrict_user/use_group policy, so the superuser short-circuit
        # in _get_policy makes a plain action_confirm() by cls.env
        # sufficient here.
        cls.school_approve = cls.env["school"].create(
            {
                "name": "School Tour Approve",
                "code": "SCHTA",
                "grade_type_id": cls.grade_type.id,
            }
        )
        cls.school_approve.action_create_analytic_account()
        cls.academic_year_approve = cls.env["school_academic_year"].create(
            {
                "name": "Year Tour Approve",
                "code": "AYTA",
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        cls.budget_approve = cls.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": cls.school_approve.id,
                "academic_year_id": cls.academic_year_approve.id,
                "user_id": cls.admin.id,
            }
        )
        cls.budget_approve.action_confirm()
        cls.budget_approve.invalidate_cache()

        # -- Cancel tour: draft budget, plus a global cancel reason so
        # it appears in the wizard's radio group regardless of model.
        cls.school_cancel = cls.env["school"].create(
            {
                "name": "School Tour Cancel",
                "code": "SCHTX",
                "grade_type_id": cls.grade_type.id,
            }
        )
        cls.academic_year_cancel = cls.env["school_academic_year"].create(
            {
                "name": "Year Tour Cancel",
                "code": "AYTX",
                "date_start": "2025-07-01",
                "date_end": "2026-06-30",
            }
        )
        cls.budget_cancel = cls.env["school_budget"].create(
            {
                "org_type": "unit",
                "school_id": cls.school_cancel.id,
                "academic_year_id": cls.academic_year_cancel.id,
                "user_id": cls.admin.id,
            }
        )
        cls.cancel_reason = cls.env["base.cancel_reason"].create(
            {
                "name": "Tour Reason",
                "code": "TOURR",
                "global_use": True,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_budget``.

        IK: docs/school_budget/01-create.md
        """
        self.start_tour("/web", "ssi_school_budget_school_budget_create", login="admin")

    def test_confirm(self):
        """Run the confirm tour for ``school_budget``.

        IK: docs/school_budget/04-confirm.md
        """
        self.start_tour(
            "/web", "ssi_school_budget_school_budget_confirm", login="admin"
        )

    def test_approve(self):
        """Run the approve tour for ``school_budget``.

        IK: docs/school_budget/05-approve.md
        """
        self.start_tour(
            "/web", "ssi_school_budget_school_budget_approve", login="admin"
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_budget``.

        IK: docs/school_budget/10-cancel.md
        """
        self.start_tour("/web", "ssi_school_budget_school_budget_cancel", login="admin")
