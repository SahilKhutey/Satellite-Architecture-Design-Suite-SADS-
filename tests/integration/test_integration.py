# SADS - Subsystems Integration Tests
import pytest
from engines.power_mod import PowerBudget, SolarArray, Battery, Load
from engines.propulsion_mod import DeltaVCalculator

def test_power_propulsion_mass_interaction():
    # Power battery dry mass limits propulsion delta-V
    battery = Battery(name="B", capacity_wh=1000.0, mass_kg=10.0)
    m_dry = 100.0 + battery.mass_kg
    m_fuel = 30.0
    
    dv = DeltaVCalculator.compute_dv(isp_s=300.0, m_dry=m_dry, m_fuel=m_fuel)
    assert dv > 0
