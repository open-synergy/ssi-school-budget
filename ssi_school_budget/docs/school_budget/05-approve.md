# Approve School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** Member of `school_budget_validator_group` (the approval template's approver\
> group)\
> **State:** `confirm` → `done`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `approve_ok` to the actor's group.
- **Access:** User is registered as an approver on the (single) approval level, which is
  always pending until approved.
- **Access:** User has _Can Approve_ access right.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the budget to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The approval template for this module has exactly one approver level, so approving it
  fulfills the whole template at once: status changes directly to **Done**, without
  passing through an intermediate approved-but-not-done state.
- The document number is generated (was a placeholder while in Draft/Waiting for
  Approval).
