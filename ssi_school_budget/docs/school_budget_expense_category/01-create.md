# Create School Budget Expense Category

> **Module:** ssi_school_budget\
> **Model:** `school_budget_expense_category`\
> **Menu:** School > Configuration > Budget > Expense Categories\
> **Actor:** Member of `school_budget_expense_category_group`\
> **State:** `—` → (no workflow state; master data)

## Pre-Condition

- **Data:** When **Direct Income** will be enabled, a target Income Category should
  already exist to map to.
- **Access:** User has _Can Create_ access right on Expense Categories.

## Flow

1. Open the **School > Configuration > Budget > Expense Categories** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Name**, **Code**, **Sequence**: Identify and order the category.
   - **Operational**: On by default. Determines whether the category counts as
     operational or non-operational expense in the Expense Simulation totals.
   - **UP Component**: When enabled, expense lines under this category are included in
     the UP (Uang Pangkal) cost base used by the tariff simulation.
   - **Direct Income**: When enabled, expense lines under this category automatically
     generate a matching income row. **Maps to Income Category** becomes required — it
     must be filled in with the income category that should receive the generated
     amount.
   - **Contribution Role**: Optional free-text label for the parent-child contribution
     mechanism.
   - **Account**: Optional. When set, this category's realized amount is pulled from
     posted journal items against that account. The same account cannot be mapped to
     more than one Income/Expense/Investment Category at a time.
4. Click **Save**.

## Post-Condition

- A new Expense Category record is created and available for selection on School Budget
  expense lines, parent expense allocations, and subsidies.
