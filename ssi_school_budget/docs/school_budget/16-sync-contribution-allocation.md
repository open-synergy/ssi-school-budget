# Sync Contribution Allocation — School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Organization Type is **Branch** or **Center** (the **Contribution
  Allocation** tab is hidden for Unit budgets).
- **Data:** Unit budgets for the same academic year (and, for a Branch budget, the same
  branch) exist to be picked up as contributors.
- **Access:** User has _Can Write_ access right on School Budget.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the Branch or Center budget and go to the **Contribution Allocation** tab.
3. Click the **Sync Contribution Allocation** button.

## Post-Condition

- One contribution allocation row exists per descendant unit budget: new units get a new
  row, and units that already had a row keep it (their **Total Student Count**, **New
  Student Count**, and any override percentage are refreshed, but the row itself is not
  recreated).
