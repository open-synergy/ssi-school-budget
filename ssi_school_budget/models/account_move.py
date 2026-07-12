# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    """
    Extends account.move so that posting, resetting to draft, or
    cancelling a journal entry triggers School Budget realization
    recompute (ssi_school_budget). account.move.line.parent_state is
    a stored related field to account.move.state, so
    action_post()/button_draft() never call AccountMoveLine.write()
    themselves - this override is what makes the state change reach
    the realization trigger.
    """

    _name = "account.move"
    _inherit = ["account.move"]

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals:
            lines = self.mapped("line_ids")
            lines._trigger_school_budget_realization(
                lines._find_affected_school_budget()
            )
        return result
