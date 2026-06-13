"""
SADS — Power Budget Module Tests
"""

import math
import pytest
from engines.power_mod.PowerBudget import PowerBudget
from engines.power_mod.SolarPanelModel import SolarArray
from engines.power_mod.BatteryModel import Battery
from engines.power_mod.LoadAnalyzer import Load


class TestPowerBudgetBalance:
    def test_budget_ok(self):
        budget = PowerBudget(
            solar_arrays=[SolarArray(name="SA", area=2.0, efficiency=0.30)],
            batteries=[Battery(name="B", capacity_wh=100.0, dod_limit=0.30)],
            loads=[Load(name="OBC", nominal_power_w=5.0)],
            eclipse_duration_min=35.0,
            orbit_period_min=95.0
        )
        bal = budget.power_balance()
        assert bal["status"] == "OK"
        assert bal["generation_w"] > bal["average_load_w"]
        assert bal["battery_margin"] > 0
