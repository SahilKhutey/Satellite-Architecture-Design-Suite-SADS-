# SADS - Integrated Structures Engine Unit Tests
import pytest
from engines.structures_engine import StructuresEngine, StructuralComponent

def test_structures_full_report():
    comp1 = StructuralComponent(name="Bus", mass_kg=80.0, position_m=[0, 0, 0])
    comp2 = StructuralComponent(name="Payload", mass_kg=40.0, position_m=[0, 0, 1.0])
    
    # Simple 3-node triangular structural truss frame
    # Node 0: fixed at (0, 0)
    # Node 1: fixed at (1, 0)
    # Node 2: free at (0.5, 0.866) (tip node)
    nodes = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.866)]
    
    # Elements: E = 70 GPa (Aluminum), Area = 1e-4 m2
    elements = [
        (0, 2, 70e9, 1e-4),
        (1, 2, 70e9, 1e-4)
    ]
    
    bc = {
        0: (True, True),
        1: (True, True)
    }
    
    # Applied force: 10 kN downwards at node 2
    forces = {
        2: (0.0, -10000.0)
    }
    
    engine = StructuresEngine(
        components=[comp1, comp2],
        nodes=nodes,
        elements=elements,
        applied_forces=forces,
        boundary_conditions=bc,
        static_g_axial=6.0,
        dynamic_g_lateral=2.0,
        stiffness_n_m=2e7
    )
    
    report = engine.report()
    
    # 1. Verify Mass properties
    assert report["total_mass_kg"] == 120.0
    assert report["center_of_mass_m"] == [0.0, 0.0, 0.3333333333333333]
    
    # 2. Verify G-loads and Vibration Natural Frequency
    assert report["launch_loads"]["equivalent_acceleration_g"] == pytest.approx(6.32455532)
    # natural freq = (1/(2pi)) * sqrt(stiffness / mass) = (1/2pi) * sqrt(2e7 / 120) = 64.97 Hz
    assert 64.0 < report["vibration_analysis"]["natural_frequency_hz"] < 66.0
    assert report["vibration_analysis"]["compliance"]["status"] == "PASSED"
    
    # 3. Verify Finite Element Analysis Results
    fe_res = report["finite_element_analysis"]
    assert fe_res is not None
    # Displacement at free node 2 (should be negative in Y direction)
    disp_y = fe_res["displacements_m"][2][1]
    assert disp_y < 0
    
    # Elements forces and stresses
    assert len(fe_res["elements"]) == 2
    # Yield limit check (stresses should be below 276 MPa for Al)
    assert report["safety_margins"]["margins_ok"] is True
