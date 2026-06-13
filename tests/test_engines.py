"""
SADS - Engine Validation Tests
Validates physics, math, and engineering correctness.
"""

import math
import pytest
from engines.power_engine import PowerBudget, SolarArray, Battery, Load, link_budget
from engines.thermal_engine import ThermalBudget, ThermalNode, Surface
from engines.propulsion_engine import PropulsionSystem, Thruster, PropellantTank, MissionManeuver, rocket_equation
from engines.comm_engine import Antenna
from engines.orbit_engine import circular_orbit, hohmann_transfer, MU_EARTH, R_EARTH


# ---------- POWER ----------
def test_solar_array_power():
    arr = SolarArray(name="Test", area=2.0, efficiency=0.30)
    p = arr.instantaneous_power(1361.0)
    assert math.isclose(p, 0.30 * 2.0 * 1361.0, rel_tol=1e-6)


def test_power_budget_surplus():
    budget = PowerBudget(
        solar_arrays=[SolarArray(name="SA", area=4.0, efficiency=0.30)],
        batteries=[Battery(name="B1", capacity_wh=100)],
        loads=[Load(name="L1", nominal_power_w=50)],
    )
    status = budget.power_balance()
    assert status["generation_w"] > status["average_load_w"]


# ---------- THERMAL ----------
def test_thermal_equilibrium():
    node = ThermalNode(
        name="Bus",
        mass_kg=10.0,
        internal_heat_w=150.0,
        surfaces=[Surface(name="Radiator", area_m2=0.5, emissivity=0.85, absorptivity=0.2)],
    )
    tb = ThermalBudget(nodes=[node], sun_view_factor=0.0, earth_view_factor=0.0)
    result = tb.report()
    t_k = result["Bus"]["temperature_k"]
    assert 250 < t_k < 350


# ---------- PROPULSION ----------
def test_rocket_equation_leo():
    res = rocket_equation(dv=9400, isp=320, dry_mass=500)
    assert res["propellant_mass_kg"] > 0
    # Falcon 9 LEO is ~9500 m/s; check reasonable mass fraction
    assert res["mass_fraction"] < 0.95


def test_propulsion_system_report():
    sys = PropulsionSystem(
        thrusters=[Thruster(name="M", isp_s=220, thrust_n=1.0)],
        tanks=[PropellantTank(name="T", mass_kg=50.0)],
        dry_mass_kg=200.0,
        maneuvers=[MissionManeuver(name="orbit_raise", delta_v_m_s=500)],
    )
    report = sys.report()
    assert report["total_delta_v_m_s"] == 500


# ---------- COMMUNICATIONS ----------
def test_link_budget_xband():
    res = link_budget(
        freq_hz=8.4e9, tx_power_w=5.0, tx_gain_dbi=15.0,
        rx_gain_dbi=35.0, distance_km=1000.0, data_rate_bps=1e6,
    )
    assert res["free_space_loss_db"] > 150
    assert "cn_margin_db" in res


def test_antenna_gain():
    ant = Antenna(diameter_m=0.5, frequency_hz=8.4e9, efficiency=0.55)
    g = ant.gain_dbi()
    # expected ~ 30 dBi for 0.5m at X-band
    assert 28 < g < 32


# ---------- ORBITAL MECHANICS ----------
def test_circular_orbit_iss():
    orb = circular_orbit(400)
    period_min = orb.orbital_period_s() / 60.0
    # ISS altitude ~ 92 min
    assert 90 < period_min < 95


def test_geo_altitude():
    geo = circular_orbit(35786)
    period_h = geo.orbital_period_s() / 3600.0
    assert math.isclose(period_h, 24.0, rel_tol=0.01)


def test_hohmann_geo_insertion():
    # LEO 200 km to GEO 35786 km
    res = hohmann_transfer(6578.0, 42164.0)
    # standard GEO insertion dV ~ 3932 m/s
    assert 3900 < res["total_dv_m_s"] < 4000


def test_kepler_third_law():
    a = R_EARTH + 500e3
    period = 2 * math.pi * math.sqrt(a ** 3 / MU_EARTH)
    # ~ 94.5 min
    assert 90 < period / 60 < 100


# ---------- AI COPILOT QUICK CHECK ----------
def test_cubesat_eclipse_feasibility():
    """Simulate a 3U cubesat with small battery."""
    budget = PowerBudget(
        solar_arrays=[SolarArray(name="Body", area=0.1, efficiency=0.30)],
        batteries=[Battery(name="Pack", capacity_wh=30, dod_limit=0.30)],
        loads=[Load(name="OBC", nominal_power_w=2.0)],
        eclipse_duration_min=35.0,
    )
    status = budget.power_balance()
    required = status["eclipse_energy_wh"]
    usable = 30 * 0.30
    margin = (usable - required) / required
    # 2W * 35/60 hr = 1.17 Wh required; 9 Wh usable = huge margin
    assert margin > 0


# ---------- STRUCTURES ----------
def test_structures_mass_properties():
    from engines.structures_engine import StructuresEngine, StructuralComponent
    comp1 = StructuralComponent(name="Bus", mass_kg=100.0, position_m=[0, 0, 0])
    comp2 = StructuralComponent(name="Payload", mass_kg=20.0, position_m=[0, 0, 1.2])
    
    engine = StructuresEngine([comp1, comp2])
    report = engine.report()
    
    assert report["total_mass_kg"] == 120.0
    assert report["center_of_mass_m"] == [0.0, 0.0, 0.2]
    assert report["inertia_tensor_kg_m2"][0][0] == pytest.approx(24.0)

