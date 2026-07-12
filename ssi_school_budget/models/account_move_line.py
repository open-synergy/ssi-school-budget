# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    """
    Extends account.move.line so that creating, editing, or deleting a
    journal item that feeds School Budget realization
    (ssi_school_budget) automatically recomputes every affected
    budget's Realization tab, instead of requiring the manual Compute
    Realization button.
    """

    _name = "account.move.line"
    _inherit = ["account.move.line"]

    @api.model
    def _get_school_budget_realization_trigger_fields(self):
        return {
            "account_id",
            "analytic_account_id",
            "date",
            "debit",
            "credit",
            "balance",
            "company_id",
            "parent_state",
            "move_id",
        }

    def _find_affected_school_budget(self):
        lines = self.filtered("analytic_account_id")
        if not lines:
            return self.env["school_budget"]
        analytic_account_ids = lines.mapped("analytic_account_id").ids
        company_ids = lines.mapped("company_id").ids
        dates = lines.mapped("date")
        return (
            self.env["school_budget"]
            .sudo()
            .search(
                [
                    ("analytic_account_id", "in", analytic_account_ids),
                    ("company_id", "in", company_ids),
                    ("academic_year_id.date_start", "<=", max(dates)),
                    ("academic_year_id.date_end", ">=", min(dates)),
                ]
            )
        )

    def _trigger_school_budget_realization(self, budgets):
        if self.env.context.get("skip_school_budget_realization"):
            return
        if budgets:
            budgets.sudo().action_compute_realization()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._trigger_school_budget_realization(
            records._find_affected_school_budget()
        )
        return records

    def write(self, vals):
        trigger_fields = self._get_school_budget_realization_trigger_fields()
        if not trigger_fields.intersection(vals):
            return super().write(vals)
        budgets_before = self._find_affected_school_budget()
        result = super().write(vals)
        budgets_after = self._find_affected_school_budget()
        self._trigger_school_budget_realization(budgets_before | budgets_after)
        return result

    def unlink(self):
        budgets = self._find_affected_school_budget()
        result = super().unlink()
        self._trigger_school_budget_realization(budgets)
        return result
