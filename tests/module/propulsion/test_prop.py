# SADS - Propulsion Module Tests
import pytest
from engines.propulsion_mod import Thruster, FuelTank, DeltaVCalculator, OrbitTransfer, PropulsionSimulation

def test_orbit_transfer_hohmann():
    trans = OrbitTransfer.hohmann(r1_km=6700.0, r2_km=42164.0)
    assert 3800.0 < trans["total_dv"] < 4000.0

def test_propulsion_simulation():
    res = PropulsionSimulation.simulate_maneuvers(isp=300.0, m_dry=200.0, m_fuel=50.0, dv_req=500.0)
    assert res["feasible"] is True

def test_propellant_mismatch_and_power():
    from engines.propulsion_engine import PropulsionSystem, Thruster, PropellantTank
    
    # 1. Compatible monoprop system
    sys1 = PropulsionSystem(
        thrusters=[Thruster(name="Monoprop Thruster", isp_s=220, thrust_n=0.5, power_w=5.0)],
        tanks=[PropellantTank(name="Hydrazine Tank", mass_kg=10.0)],
        dry_mass_kg=100.0
    )
    report1 = sys1.report()
    assert report1["propellant_match_ok"] is True
    assert report1["total_power_w"] == 5.0

    # 2. Mismatched system (electric thruster + chemical tank)
    sys2 = PropulsionSystem(
        thrusters=[Thruster(name="Hall Effect Ion Engine", isp_s=1650, thrust_n=0.08, power_w=150.0)],
        tanks=[PropellantTank(name="Hydrazine Tank", mass_kg=10.0)],
        dry_mass_kg=100.0
    )
    report2 = sys2.report()
    assert report2["propellant_match_ok"] is False
    assert report2["total_power_w"] == 150.0

