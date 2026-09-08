# Restart School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** Member of `school_budget_validator_group`\
> **State:** `cancel` | `reject` → `draft`\
> **Requires:** `10-cancel`

## Pre-Condition

- **Record:** Status is **Cancelled** or **Rejected**.
- **Config:** An active `policy.template` grants `restart_ok` for that state to the
  actor's group.
- **Access:** User has _Can Restart_ access right.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the budget to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status returns to **Draft**.
- All approval records are removed. A later Confirm starts the approval process from the
  beginning.

> **Note:** This module also defines a separate `restart_approval_ok` policy field for\
> the mixin's "Restart Approval Process" button. That button is guarded by `not\ document.approval_template_id`,
> and this module registers `approval_template_school_budget`\
> unconditionally for every `school_budget` record — so the guard is permanently false
> and\
> the button never appears. There is no `11-restart-approval.md` IK for this reason (see\
> the `odoo-development` skill's `08-templates.md`, section on what the\
> `approval_template_id` guard does).
