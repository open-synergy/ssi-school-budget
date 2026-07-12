# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Budget",
    "version": "14.0.15.0.0",
    "website": "https://simetri-sinergi.id",
    # pylint: disable=line-too-long
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia, Odoo Community Association (OCA)",  # noqa: B950
    # pylint: enable=line-too-long
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_school",
        "ssi_master_data_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_decorator",
        "ssi_financial_accounting",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/res_group/school_budget.xml",
        "security/ir_model_access/school_budget_income_category.xml",
        "security/ir_model_access/school_budget_expense_category.xml",
        "security/ir_model_access/school_budget_investment_category.xml",
        "security/ir_model_access/school_budget.xml",
        "security/ir_rule/school_budget.xml",
        "ir_sequence/school_budget.xml",
        "sequence_template/school_budget.xml",
        "approval_template/school_budget.xml",
        "policy_template/school_budget.xml",
        "menu.xml",
        "views/school_budget_income_category.xml",
        "views/school_budget_expense_category.xml",
        "views/school_budget_investment_category.xml",
        "views/res_company.xml",
        "views/school_branch.xml",
        "views/school.xml",
        "views/school_budget.xml",
    ],
}
