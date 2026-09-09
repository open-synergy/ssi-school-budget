# Create School Branch

> **Module:** ssi_school_budget\
> **Extends:** ssi_school — model `school_branch`, aksi `01-create`

## Additional Fields

When this module is installed, the create form gains two fields:

- **Analytic Group**: The Analytic Group under which this branch's school units'
  analytic accounts are nested, for roll-up reporting. Optional at creation; set it
  before using **Create Analytic Account** (see `07-create-analytic-account.md`) if
  roll-up grouping is needed.
- **Analytic Account**: Read-only. Filled in later by **Create Analytic Account**, not
  entered directly here.
