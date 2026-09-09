# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolBudgetExpenseCategory(HttpSavepointCase):
    """Tour test for the ``school_budget_expense_category`` work
    instructions.
    """

    def test_create(self):
        """Run the create tour for ``school_budget_expense_category``.

        IK: docs/school_budget_expense_category/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_budget_school_budget_expense_category_create",
            login="admin",
        )
