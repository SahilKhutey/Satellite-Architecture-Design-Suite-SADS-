"""
SADS — Power Validator Module Tests
"""

import pytest
from engines.power_mod.PowerValidator import PowerValidator
from engines.power_mod.PowerBudget import PowerBudget
from engines.power_mod.SolarPanelModel import SolarArray
from engines.power_mod.BatteryModel import Battery
from engines.power_mod.LoadAnalyzer import Load


class TestPowerValidator:
    def test_validation_pass(self):
        budget = PowerBudget(
            solar_arrays=[SolarArray(name="SA", area=2.0, efficiency=0.30)],
            batteries=[Battery(name="B", capacity_wh=100.0, dod_limit=0.50)],
            loads=[Load(name="OBC", nominal_power_w=5.0)],
            eclipse_duration_min=30.0,
            orbit_period_min=90.0
        )
        assert PowerValidator.validate_margins(budget) is True

    def test_validation_fail_insufficient_generation(self):
        budget = PowerBudget(
            solar_arrays=[SolarArray(name="SA", area=0.01, efficiency=0.30)],
            batteries=[Battery(name="B", capacity_wh=10.0, dod_limit=0.30)],
            loads=[Load(name="payload", nominal_power_w=50.0)],
            eclipse_duration_min=30.0,
            orbit_period_min=90.0
        )
        # Margin is < 20%
        assert PowerValidator.validate_margins(budget) is False
