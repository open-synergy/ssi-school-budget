# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo_yaml_test import YamlTransactionCase


@tagged("post_install", "-at_install")
class TestSchoolBudgetSimulation(YamlTransactionCase):
    def test_school_budget_simulation(self):
        self.run_yaml_scenario("test_data_school_budget_simulation.yaml")
