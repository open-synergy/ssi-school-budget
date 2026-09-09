# Confirm School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **State:** `draft` → `confirm`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Record:** The organization has an Analytic Account (Unit: the school's; Branch: the
  branch's; Center: the company's). Confirm is blocked with an error if it is missing —
  see the extension IK under `school`/`school_branch` for how to create one.
- **Config:** An active `policy.template` for `school_budget` grants `confirm_ok` for
  state `draft` to the actor's group.
- **Config:** An active `approval.template` for `school_budget` matches this record and
  has at least one approver level.
- **Config:** An active `sequence.template` exists for `school_budget`.
- **Access:** User has _Can Confirm_ access right.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the budget to confirm.
3. Click the **Confirm** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Waiting for Approval**.
- Approval records are created for each approver level defined by the approval template.
