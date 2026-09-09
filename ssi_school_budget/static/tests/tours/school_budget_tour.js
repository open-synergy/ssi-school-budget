/* Copyright 2026 OpenSynergy Indonesia
 * Copyright 2026 PT. Simetri Sinergi Indonesia
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("ssi_school_budget.school_budget_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/school_budget/01-create.md
    tour.register(
        "ssi_school_budget_school_budget_create",
        {
            test: true,
            url: "/web",
        },
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Budget menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.menu_school_budget_budget"]',
            },
            {
                content: "Open the Budgets menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.school_budget_menu"]',
            },
            {
                content: "Budgets list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Budgets)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Click Create",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Select the School",
                trigger: ".o_field_many2one[name='school_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text School Tour Create",
            },
            {
                content: "Pick School Tour Create from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(School Tour Create)",
                in_modal: false,
            },
            {
                content: "Select the Academic Year",
                trigger: ".o_field_many2one[name='academic_year_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Year Tour Create",
            },
            {
                content: "Pick Year Tour Create from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a:contains(Year Tour Create)",
                in_modal: false,
            },
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Status is Draft",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/school_budget/04-confirm.md
    tour.register(
        "ssi_school_budget_school_budget_confirm",
        {
            test: true,
            url: "/web",
        },
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Budget menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.menu_school_budget_budget"]',
            },
            {
                content: "Open the Budgets menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.school_budget_menu"]',
            },
            {
                content: "Budgets list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Budgets)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Open the budget to confirm",
                trigger: ".o_data_row:contains(Year Tour Confirm) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Click the Confirm button",
                trigger: ".o_statusbar_buttons button[name='action_confirm']",
                extra_trigger: ".o_form_view",
            },
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },
            {
                content: "Status is Waiting for Approval",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                extra_trigger: "body:not(:has(.modal))",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/school_budget/05-approve.md
    tour.register(
        "ssi_school_budget_school_budget_approve",
        {
            test: true,
            url: "/web",
        },
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Budget menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.menu_school_budget_budget"]',
            },
            {
                content: "Open the Budgets menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.school_budget_menu"]',
            },
            {
                content: "Budgets list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Budgets)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Open the budget to approve",
                trigger: ".o_data_row:contains(Year Tour Approve) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Click the Approve button",
                trigger: ".o_statusbar_buttons button[name='action_approve_approval']",
                extra_trigger: ".o_form_view",
            },
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },
            {
                content: "Status is Done",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                extra_trigger: "body:not(:has(.modal))",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/school_budget/10-cancel.md
    tour.register(
        "ssi_school_budget_school_budget_cancel",
        {
            test: true,
            url: "/web",
        },
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Budget menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.menu_school_budget_budget"]',
            },
            {
                content: "Open the Budgets menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.school_budget_menu"]',
            },
            {
                content: "Budgets list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Budgets)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Open the budget to cancel",
                trigger: ".o_data_row:contains(Year Tour Cancel) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Click the Cancel button",
                trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                extra_trigger: ".o_form_view",
            },
            {
                content: "Wizard is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Select the cancellation reason",
                trigger:
                    ".o_field_widget[name='cancel_reason_id'] .o_radio_item:contains(Tour Reason) input",
            },
            {
                content: "Confirm the wizard",
                trigger: ".modal-footer button[name='action_confirm']",
            },
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
            },
            {
                content: "Status is Cancelled",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                extra_trigger: "body:not(:has(.modal))",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
