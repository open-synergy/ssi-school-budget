# Create School Budget

> **Module:** ssi_school_budget\
> **Model:** `school_budget`\
> **Menu:** School > Budget > Budgets\
> **Actor:** School Budget / User (`school_budget_user_group`)\
> **State:** `—` → `draft`

## Pre-Condition

- **Config:** An active `sequence.template` exists for `school_budget` (used to number
  the document once it reaches Done).
- **Config:** An active `policy.template` for `school_budget` grants `confirm_ok` for
  state `draft` to the actor's group (needed later, at Confirm).
- **Data:** A `school_academic_year` record exists for the year being budgeted.
- **Data:** For a Unit budget, the `school` record must already exist. For a Branch
  budget, the `school_branch` record must already exist.
- **Access:** User has _Can Create_ access right on School Budget.

## Flow

1. Open the **School > Budget > Budgets** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Organization Type**: Choose **Unit**, **Branch**, or **Center**. This determines
     which organization fields are shown next.
   - **School**: Required and shown only when Organization Type is **Unit**. Selecting a
     school automatically fills in **Branch** (read-only) and seeds the **Student
     Assumption** tab with one row per grade of the school's grade type.
   - **Branch**: Required and shown only when Organization Type is **Branch**. Not shown
     for **Center**.
   - **Academic Year**: The academic year this budget covers. Also determines the
     computed **Fiscal Year** field.
4. Click **Save**.

## Post-Condition

- A new School Budget record is created in **Draft** status.
- Only one budget may exist per organization and academic year; a duplicate attempt is
  rejected.
