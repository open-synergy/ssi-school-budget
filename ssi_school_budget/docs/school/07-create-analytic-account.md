# Create Analytic Account — School

> **Module:** ssi_school_budget\
> **Extends:** ssi_school — model `school`\
> **Model:** `school`\
> **Menu:** School > Configuration > Grade > Schools\
> **Actor:** Member of `school_group`\
> **Requires:** `ssi_school` module's own School create/edit IK (`01-create.md`)

## Pre-Condition

- **Record:** The school's **Analytic Account** field is empty. Once set, the button
  disappears (it is idempotent — clicking it again when already set does nothing).
- **Access:** User has _Can Write_ access right on School.

## Flow

1. Open the **School > Configuration > Grade > Schools** menu.
2. Open the school.
3. Click the **Create Analytic Account** smart button in the button box.

## Post-Condition

- A new `account.analytic.account` record is created and linked as this school's
  **Analytic Account** (shown read-only on the form). It is nested under the school's
  branch's Analytic Group when the school belongs to a branch, otherwise under the
  company's School Budget Analytic Group.
- A School Budget for this school (Organization Type = Unit) can now be confirmed — see
  `ssi_school_budget/docs/school_budget/04-confirm.md`.
- The same analytic account cannot later be assigned to another school, a branch, or a
  company's School Budget Analytic Account — such a change is rejected.
