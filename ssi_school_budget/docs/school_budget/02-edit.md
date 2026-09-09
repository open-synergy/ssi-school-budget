# Edit School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Access:** User has _Can Write_ access right on School Budget.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Find and open the budget to edit.
3. Change the fields on the **Student Assumption**, **Expense**, **Income**,
   **Investment**, **Old Asset**, **Financial Investment**, **Parent Cost Allocation**,
   **Contribution Allocation**, **Subsidy**, and **Direct Income Override** tabs as
   needed, depending on the Organization Type.
4. Click **Save**.

## Post-Condition

- The record is updated with the new values.
- Totals shown elsewhere on the form (e.g. total expense, total student count) recompute
  automatically from the edited lines.
