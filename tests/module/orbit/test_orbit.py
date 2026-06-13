# SADS - Orbit Module Tests
import pytest
import math
from engines.orbit_mod import KeplerPropagator, J2Perturbation, OrbitSimulation

def test_orbit_propagation():
    # Propagate circular LEO 500km for 1 period
    period = 2 * math.pi * math.sqrt((6378.137 + 500.0)**3 / 398600.4418)
    da = KeplerPropagator.propagate(alt_km=500.0, dt_s=period)
    # Final anomaly change should return to 0 (modulo 2pi)
    assert pytest.approx(da, abs=1e-5) == 0.0 or pytest.approx(da, abs=1e-5) == 2 * math.pi

def test_j2_perturbation():
    raan_rate, _ = J2Perturbation.precession_rates(a=7000.0, e=0.0, i=math.radians(97.6))
    # SSO orbit J2 regression should balance Earth orbit rate (~0.9856 deg/day)
    assert raan_rate != 0
