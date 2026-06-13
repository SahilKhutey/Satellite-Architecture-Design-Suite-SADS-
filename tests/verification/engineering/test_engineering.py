# SADS - Engineering Rules Verification
import pytest
from engines.power_mod import PowerValidator, PowerBudget, SolarArray, Battery, Load

def test_engineering_margins():
    budget = PowerBudget(
        solar_arrays=[SolarArray(name="SA", area=2.0, efficiency=0.30)],
        batteries=[Battery(name="B", capacity_wh=100.0, dod_limit=0.50)],
        loads=[Load(name="OBC", nominal_power_w=5.0)],
        eclipse_duration_min=30.0,
        orbit_period_min=90.0
    )
    # Power margins must satisfy 20% rule
    assert PowerValidator.validate_margins(budget) is True
