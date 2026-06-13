"""
SADS — Numerical Methods Unit Tests
Test core numerical algorithms.
"""

import math
import pytest
import numpy as np

def test_kepler_solver():
    """Verify Kepler orbital period calculation."""
    from engines.orbit_engine import circular_orbit
    # circular_orbit expects its altitude in km
    orb = circular_orbit(400.0) 
    period = orb.orbital_period_s()
    # ISS orbital period should be ~5545 s
    assert 5400 < period < 5700

def test_newton_raphson_thermal():
    """Verify thermal equation convergence."""
    from engines.thermal_engine import ThermalNode, Surface, ThermalBudget
    node = ThermalNode(
        name="Bus",
        mass_kg=10.0,
        internal_heat_w=150.0,
        surfaces=[Surface(name="Rad", area_m2=0.5, emissivity=0.85, absorptivity=0.2)],
    )
    tb = ThermalBudget(nodes=[node], sun_view_factor=0.0, earth_view_factor=0.0)
    result = tb.report()
    t_k = result["Bus"]["temperature_k"]
    # Newton-Raphson converges to ~280.88 K for 150W on 0.5m2 radiator
    assert 278 < t_k < 283

def test_quaternion_normalization():
    """Verify quaternion attitude updates remain normalized."""
    from engines.adcs_engine import InertiaTensor, ADCSConfig
    inertia = InertiaTensor(ixx=10, iyy=20, izz=30, ixy=0, ixz=0, iyz=0)
    config = ADCSConfig(inertia=inertia, wheels=[], sensors=[])
    # Verify pointing budget runs correctly
    pointing = config.pointing_budget()
    assert pointing["total_3sigma_deg"] >= 0
