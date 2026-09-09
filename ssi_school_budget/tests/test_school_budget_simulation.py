# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolBudgetSimulation(YamlTransactionCase):
    """YAML scenario test for the UP/US tariff simulation."""

    def test_school_budget_simulation(self):
        """Run the school_budget_simulation YAML scenario."""
        self.run_yaml_scenario("test_data_school_budget_simulation.yaml")
