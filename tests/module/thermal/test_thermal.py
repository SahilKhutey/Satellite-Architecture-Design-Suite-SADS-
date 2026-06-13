# SADS - Thermal Module Tests
import pytest
from engines.thermal_mod import ThermalNode, Surface, ThermalNetwork, ThermalSolver, ThermalValidator

def test_thermal_hot_cold_cases():
    # Set view_factor_sun=1.0 so solar flux absorption is non-zero in sunlight
    surf = Surface(name="Rad", area_m2=0.5, emissivity=0.85, absorptivity=0.2, view_factor_sun=1.0)
    # Set internal_heat_w=15.0 so it doesn't fall below structural threshold (150K) in cold shadow
    node = ThermalNode(name="Core", mass_kg=10.0, internal_heat_w=15.0, surfaces=[surf])
    net = ThermalNetwork(nodes=[node])
    
    # Hot case solar flux (1400 W/m^2)
    ThermalSolver.solve_equilibrium(net, solar_flux=1400.0)
    hot_temp = node.temperature_k
    assert hot_temp > 250.0
    
    # Cold case shadow (no solar flux)
    ThermalSolver.solve_equilibrium(net, solar_flux=0.0)
    cold_temp = node.temperature_k
    assert cold_temp < hot_temp
    
    # Validator checks structural limits (150K < T < 400K)
    assert ThermalValidator.validate_temperatures(net) is True
