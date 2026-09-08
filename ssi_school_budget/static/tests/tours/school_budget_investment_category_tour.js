/* Copyright 2026 OpenSynergy Indonesia
 * Copyright 2026 PT. Simetri Sinergi Indonesia
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("ssi_school_budget.school_budget_investment_category_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/school_budget_investment_category/01-create.md
    tour.register(
        "ssi_school_budget_school_budget_investment_category_create",
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
                content: "Open the Configuration menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school.menu_school_configuration"]',
            },
            {
                // Level 3 "Budget" has children, so it renders as a
                // non-clickable dropdown header; this leaf is
                // flattened into the same Configuration dropdown.
                content: "Open the Investment Categories menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_budget.school_budget_investment_category_menu"]',
            },
            {
                content: "Investment Categories list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Investment Categories)",
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
                content: "Fill in Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Tour Investment Category",
            },
            {
                content: "Ensure Code is /",
                trigger: ".o_field_widget[name='code']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text /",
            },
            {
                content: "Fill in Default Economic Life",
                trigger: ".o_field_widget[name='default_economic_life']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text 4",
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
        ]
    );
});
