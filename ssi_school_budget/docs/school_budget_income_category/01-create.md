# Create School Budget Income Category

> **Module:** ssi_school_budget\
> **Model:** `school_budget_income_category`\
> **Menu:** School > Configuration > Budget > Income Categories\
> **Actor:** Member of `school_budget_income_category_group`\
> **State:** `—` → (no workflow state; master data)

## Pre-Condition

- **Access:** User has _Can Create_ access right on Income Categories.

## Flow

1. Open the **School > Configuration > Budget > Income Categories** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name**, **Code**: Identify the category.
   - **Calculation Method**: How the simulation engine computes this category's amount —
     **Manual** (entered directly on an income line), **Simulated - Uang Pangkal (UP)**,
     **Simulated - Uang Sekolah (US)**, **From Direct Income Expense Category**, **Grade
     Based**, or **Sum From BOS**.
   - **Account**: Optional. When set, this category's realized amount is pulled from
     posted journal items against that account. The same account cannot be mapped to
     more than one Income/Expense/Investment Category at a time.
4. Click **Save**.

## Post-Condition

- A new Income Category record is created and available for selection on School Budget
  income lines and results.
