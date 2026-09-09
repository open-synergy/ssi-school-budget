# Create Analytic Account — School Branch

> **Module:** ssi_school_budget\
> **Extends:** ssi_school — model `school_branch`\
> **Model:** `school_branch`\
> **Menu:** School > Configuration > Branches\
> **Actor:** Member of `school_branch_group`\
> **Requires:** `ssi_school` module's own School Branch create/edit IK, and this\
> module's `01-create.md` delta (for **Analytic Group**)

## Pre-Condition

- **Record:** The branch's **Analytic Account** field is empty. Once set, the button
  disappears (it is idempotent — clicking it again when already set does nothing).
- **Access:** User has _Can Write_ access right on School Branch.

## Flow

1. Open the **School > Configuration > Branches** menu.
2. Open the branch.
3. Click the **Create Analytic Account** smart button in the button box.

## Post-Condition

- A new `account.analytic.account` record is created and linked as this branch's
  **Analytic Account** (shown read-only on the form), nested under the branch's own
  **Analytic Group**.
- A School Budget for this branch (Organization Type = Branch) can now be confirmed —
  see `ssi_school_budget/docs/school_budget/04-confirm.md`.
- The same analytic account cannot later be assigned to another branch, a school, or a
  company's School Budget Analytic Account — such a change is rejected.
