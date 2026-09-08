# Simulate School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Organization Type is set (the button is hidden otherwise). Available in
  any status, including after Done — running it again recomputes the results from the
  current data.
- **Access:** User has _Can Write_ access right on School Budget.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Open the budget to simulate.
3. Click the **Simulate** button next to the status bar.

## Post-Condition

- The **UP Simulation**, **US Simulation**, **Income Simulation**, **Expense
  Simulation**, and (for Branch/Center) **Allocation** and **Comparative Summary** tabs
  are rebuilt from the current Student Assumption, Expense, Income, Investment, Old
  Asset, Financial Investment, and (for Unit) Parent Cost Allocation data.
- Running Simulate again replaces the previous simulation rows; it does not accumulate
  duplicates.
