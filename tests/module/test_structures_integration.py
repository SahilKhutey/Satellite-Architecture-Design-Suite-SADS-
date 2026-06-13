# SADS - Structures Engine Integration Tests
import pytest
from engines.structures_engine import StructuresEngine, StructuralComponent

def test_structures_launcher_profiles():
    # Verify structures audits work under different launcher G-load conditions
    comp_bus = StructuralComponent(name="Bus Structure", mass_kg=120.0, position_m=[0, 0, 0])
    comp_panel = StructuralComponent(name="Solar Panel", mass_kg=20.0, position_m=[1.5, 0, 0])
    
    # Define simple truss nodes
    nodes = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5)]
    elements = [
        (0, 2, 70e9, 1e-4),
        (1, 2, 70e9, 1e-4)
      ]
    bc = {0: (True, True), 1: (True, True)}

    # Launcher Profile 1: Falcon 9 (6.0G axial, 2.0G lateral)
    engine_f9 = StructuresEngine(
        components=[comp_bus, comp_panel],
        nodes=nodes,
        elements=elements,
        boundary_conditions=bc,
        static_g_axial=6.0,
        dynamic_g_lateral=2.0
    )
    report_f9 = engine_f9.report()
    assert report_f9["total_mass_kg"] == 140.0
    assert report_f9["launch_loads"]["equivalent_acceleration_g"] == pytest.approx(6.32455532)
    assert report_f9["safety_margins"]["margins_ok"] is True

    # Launcher Profile 2: Electron (8.0G axial, 3.0G lateral)
    engine_elec = StructuresEngine(
        components=[comp_bus, comp_panel],
        nodes=nodes,
        elements=elements,
        boundary_conditions=bc,
        static_g_axial=8.0,
        dynamic_g_lateral=3.0
    )
    report_elec = engine_elec.report()
    assert report_elec["launch_loads"]["equivalent_acceleration_g"] == pytest.approx(8.5440037)
    # Stresses are higher, but Area is large enough so margins should be fine
    assert report_elec["safety_margins"]["margins_ok"] is True
