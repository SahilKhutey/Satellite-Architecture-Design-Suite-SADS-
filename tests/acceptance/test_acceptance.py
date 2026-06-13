# SADS - System-Level Acceptance Tests
import pytest
from mbse.RequirementsManager import RequirementsManager, Requirement
from mbse.TraceabilityEngine import TraceabilityEngine
from mbse.VerificationMatrix import VerificationMatrix
from mbse.ComplianceEngine import ComplianceEngine
from ai.ArchitectureAdvisor import ArchitectureAdvisor
from ai.OptimizationAgent import OptimizationAgent
from digital_twin.StateSynchronizer import StateSynchronizer

def test_system_acceptance_flow():
    # 1. MBSE Compliance Flow Acceptance
    rm = RequirementsManager()
    te = TraceabilityEngine()
    
    # Define a mass limit requirement of 150 kg
    req_mass = Requirement(id="REQ-001", name="MassLimit", category="mass", limit_value=150.0, operator="less_than")
    rm.add_requirement(req_mass)
    te.add_trace("REQ-001", "Bus")
    te.add_trace("REQ-001", "Payload")
    
    # Subsystem actual masses
    measured_masses = {"Bus": 80.0, "Payload": 50.0}
    
    # Verify
    verification_results = VerificationMatrix.verify_all(rm, te, measured_masses)
    assert len(verification_results) == 1
    assert verification_results[0]["requirement_id"] == "REQ-001"
    assert verification_results[0]["satisfied"] is True
    assert verification_results[0]["measured_value"] == 130.0
    
    # Generate compliance log
    log = ComplianceEngine.generate_signoff_log(verification_results)
    assert "PASSED" in log
    assert "REQ-001" in log

    # 2. AI Advisor Sizing Flow Acceptance
    recs = ArchitectureAdvisor.analyze_margins(power_margin=0.15, thermal_margin_k=8.0, pointing_error_deg=0.15)
    assert len(recs) == 3
    assert any("power margin" in r.lower() for r in recs)
    
    opt = OptimizationAgent.optimize_eps(load_w=100.0, eclipse_min=35.0)
    assert opt["battery_wh"] > 0
    assert opt["panel_w"] == 200.0

    # 3. Digital Twin Synchronization Flow Acceptance
    # Start with initial estimate, apply sensor update, check convergence
    est_temp = 25.0
    measured_temp = 27.0
    synced_temp = StateSynchronizer.filter_step(est_temp, measured_temp, gain=0.1)
    assert synced_temp == 25.2

    # 4. Structures Subsystem API Acceptance
    from api.main import structures_subsystem
    struct_data = structures_subsystem()
    assert struct_data["satellite_name"] == "SADS-Demo-1"
    assert len(struct_data["components"]) > 0
    total_mass = sum(c["mass_kg"] for c in struct_data["components"])
    assert total_mass > 0

