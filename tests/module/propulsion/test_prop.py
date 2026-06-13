# SADS - Propulsion Module Tests
import pytest
from engines.propulsion_mod import Thruster, FuelTank, DeltaVCalculator, OrbitTransfer, PropulsionSimulation

def test_orbit_transfer_hohmann():
    trans = OrbitTransfer.hohmann(r1_km=6700.0, r2_km=42164.0)
    assert 3800.0 < trans["total_dv"] < 4000.0

def test_propulsion_simulation():
    res = PropulsionSimulation.simulate_maneuvers(isp=300.0, m_dry=200.0, m_fuel=50.0, dv_req=500.0)
    assert res["feasible"] is True
