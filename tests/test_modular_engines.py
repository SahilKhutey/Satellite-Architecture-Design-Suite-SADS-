# SADS - Modular Subsystem Engine Verification Tests
import importlib
import pytest
import math

def test_modular_power():
    power_mod = importlib.import_module("engines.power-engine")
    arr = power_mod.SolarArray(name="TestArray", area=2.0, efficiency=0.30)
    p = arr.instantaneous_power(1361.0)
    assert math.isclose(p, 2.0 * 0.30 * 1361.0)

def test_modular_thermal():
    thermal_mod = importlib.import_module("engines.thermal-engine")
    surf = thermal_mod.Surface(name="Rad", area_m2=0.5, emissivity=0.8, absorptivity=0.2)
    node = thermal_mod.ThermalNode(name="Core", mass_kg=10.0, surfaces=[surf])
    net = thermal_mod.ThermalNetwork(nodes=[node])
    
    # Run solver
    thermal_mod.ThermalSolver.solve_equilibrium(net)
    assert node.temperature_k > 0

def test_modular_comms():
    comm_mod = importlib.import_module("engines.communications-engine")
    ant = comm_mod.Antenna(diameter_m=0.5, frequency_hz=8.4e9)
    gain = ant.gain_dbi()
    assert 28.0 < gain < 32.0

def test_modular_propulsion():
    prop_mod = importlib.import_module("engines.propulsion-engine")
    dv = prop_mod.DeltaVCalculator.compute_dv(isp_s=300.0, m_dry=200.0, m_fuel=50.0)
    assert dv > 0

def test_modular_adcs():
    adcs_mod = importlib.import_module("engines.adcs-engine")
    error = adcs_mod.AttitudeSimulator.simulate_pointing_error(wheels_count=4)
    assert error < 0.05

def test_modular_orbit():
    orbit_mod = importlib.import_module("engines.orbit-engine")
    raan_rate, _ = orbit_mod.J2Perturbation.precession_rates(a=7000.0, e=0.0, i=math.radians(51.6))
    assert raan_rate != 0
