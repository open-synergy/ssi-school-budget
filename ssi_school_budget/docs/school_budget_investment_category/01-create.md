# Create School Budget Investment Category

> **Module:** ssi_school_budget\
> **Model:** `school_budget_investment_category`\
> **Menu:** School > Configuration > Budget > Investment Categories\
> **Actor:** Member of `school_budget_investment_category_group`\
> **State:** `—` → (no workflow state; master data)

## Pre-Condition

- **Access:** User has _Can Create_ access right on Investment Categories.

## Flow

1. Open the **School > Configuration > Budget > Investment Categories** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name**, **Code**: Identify the category.
   - **Default Economic Life**: Number of years, greater than zero. Used to prefill
     **Useful Life** when this category is selected on a new investment line.
   - **Account**: Optional. When set, this category's realized amount is pulled from
     posted journal items against that account. The same account cannot be mapped to
     more than one Income/Expense/Investment Category at a time.
4. Click **Save**.

## Post-Condition

- A new Investment Category record is created and available for selection on School
  Budget investment lines.
