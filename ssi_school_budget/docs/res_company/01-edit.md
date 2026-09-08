# Edit Company — School Budget Analytic Account

> **Module:** ssi_school_budget\
> **Extends:** base — model `res.company` (Settings > Companies > Company form; `base`\
> is core Odoo and does not publish an SSI-style numbered IK to anchor to, so this file\
> documents the added fields directly rather than as a delta on a specific base aksi)\
> **Menu:** Settings > Users & Companies > Companies\
> **Actor:** Member of `base.group_system` (Settings access)

## Additional Fields

When this module is installed, the company form (Settings > Users & Companies >
Companies > open a company) gains a **School Budget** group with two fields:

- **School Budget Analytic Account**: The Analytic Account representing this company (as
  the Center in the school organization hierarchy) on School Budget realization. Must
  not be shared with any branch or school unit — assigning an account already used
  elsewhere is rejected. Optional; a Center-organization School Budget cannot be
  confirmed until it is set (see `ssi_school_budget/docs/school_budget/04-confirm.md`).
  Selected from existing `account.analytic.account` records — unlike School/School
  Branch, there is no create-account button here.
- **School Budget Analytic Group**: The root Analytic Group under which branch/unit
  analytic groups are nested, for roll-up reporting. Optional.

## Additional Post-Condition

- The company's School Budget Analytic Account/Group are updated after Save.
