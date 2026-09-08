# Compute Realization — School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** None — available in any status.
- **Data:** Expense and Income Categories that should be tracked against the ledger have
  their **Account** field set; only those categories are pulled.
- **Access:** User has _Can Write_ access right on School Budget.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the budget and go to the **Realization** tab.
3. Click the **Compute Realization** button.

## Post-Condition

- The **Realization** tab's Expense Realization and Income Realization tables are
  rebuilt from posted `account.move.line` entries, one row per (category, month).
- The **Budget vs Actual** tab (budget amount, realized amount, variance, absorption
  rate) recomputes from the refreshed realization rows.
- Running Compute Realization again replaces the previous rows.
