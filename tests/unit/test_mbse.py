# SADS MBSE Unit Tests
import pytest
from mbse.InterfaceDefinitions import Port
from mbse.ComplianceEngine import ComplianceEngine

def test_port_compatibility_audit():
    # Define blocks and their ports
    blocks = {
        "EPS": [
            Port(name="Power_Out", port_type="output", flow_type="power", capacity=120.0),
            Port(name="Telem_Out", port_type="output", flow_type="data", capacity=1000.0)
        ],
        "OBC": [
            Port(name="Power_In", port_type="input", flow_type="power", capacity=50.0),
            Port(name="Telemetry", port_type="input", flow_type="data", capacity=9600.0)
        ]
    }
    
    # 1. Compatible connection (EPS Power_Out -> OBC Power_In)
    conn_power = {"from_block": "EPS", "from_port": "Power_Out", "to_block": "OBC", "to_port": "Power_In"}
    results = ComplianceEngine.audit_ports_compatibility(blocks, [conn_power])
    assert len(results) == 1
    assert results[0]["compatible"] is True
    
    # 2. Incompatible connection (flow type mismatch)
    conn_bad_flow = {"from_block": "EPS", "from_port": "Telem_Out", "to_block": "OBC", "to_port": "Power_In"}
    results_bad_flow = ComplianceEngine.audit_ports_compatibility(blocks, [conn_bad_flow])
    assert results_bad_flow[0]["compatible"] is False
    assert "Flow types do not match" in results_bad_flow[0]["reason"]
    
    # 3. Incompatible connection (capacity mismatch: EPS output 1000 < OBC input requirement 9600)
    conn_bad_cap = {"from_block": "EPS", "from_port": "Telem_Out", "to_block": "OBC", "to_port": "Telemetry"}
    results_bad_cap = ComplianceEngine.audit_ports_compatibility(blocks, [conn_bad_cap])
    assert results_bad_cap[0]["compatible"] is False
    assert "Capacity mismatch" in results_bad_cap[0]["reason"]


def test_sysml_co_simulation():
    import json
    from mbse.CoSimulation import SysMLCoSimulator

    sysml_blocks = {
        "blocks": [
            {
                "name": "PrimarySolarArray",
                "type": "SolarArray",
                "properties": {
                    "area_m2": 2.5,
                    "efficiency": 0.28
                },
                "requirements": [
                    {
                        "id": "REQ-001",
                        "name": "Solar Array Power Generation Limit",
                        "category": "power",
                        "limit_value": 500.0,
                        "operator": "greater_than"
                    }
                ]
            },
            {
                "name": "MainBattery",
                "type": "Battery",
                "properties": {
                    "capacity_wh": 120.0,
                    "dod_limit": 0.50
                },
                "requirements": [
                    {
                        "id": "REQ-002",
                        "name": "Battery Usable Capacity Limit",
                        "category": "power",
                        "limit_value": 50.0,
                        "operator": "greater_than"
                    }
                ]
            },
            {
                "name": "OBC_Payload_Load",
                "type": "Load",
                "properties": {
                    "power_draw_w": 50.0
                }
            },
            {
                "name": "Total_Generation",
                "type": "PowerMetric",
                "properties": {},
                "requirements": [
                    {
                        "id": "REQ-003",
                        "name": "Total Generation Target",
                        "category": "power",
                        "limit_value": 800.0,
                        "operator": "greater_than"
                    }
                ]
            },
            {
                "name": "Battery_Margin",
                "type": "PowerMetric",
                "properties": {},
                "requirements": [
                    {
                        "id": "REQ-004",
                        "name": "Battery Margin Target",
                        "category": "power",
                        "limit_value": 0.0,
                        "operator": "greater_than"
                    }
                ]
            }
        ]
    }

    json_str = json.dumps(sysml_blocks)
    result = SysMLCoSimulator.run_sysml_co_simulation(json_str, altitude_km=500.0)

    # 1. Verify orbit parameters are calculated correctly
    assert "orbit_parameters" in result
    orbit_params = result["orbit_parameters"]
    assert orbit_params["altitude_km"] == 500.0
    assert orbit_params["period_min"] > 90.0 and orbit_params["period_min"] < 100.0
    assert orbit_params["eclipse_min"] > 30.0 and orbit_params["eclipse_min"] < 40.0

    # 2. Verify solver report (power budget)
    assert "solver_report" in result
    power_report = result["solver_report"]
    assert power_report["generation_w"] == pytest.approx(0.28 * 2.5 * 1361.0)
    assert power_report["average_load_w"] == 50.0
    assert "battery_margin" in power_report

    # 3. Verify requirements checking
    assert "verification_results" in result
    verification = result["verification_results"]
    assert len(verification) == 4

    # Check that REQ-001 (SolarArray power: 952.7 > 500.0 limit) is satisfied
    req1 = next(r for r in verification if r["requirement_id"] == "REQ-001")
    assert req1["satisfied"] is True
    assert req1["measured_value"] == pytest.approx(0.28 * 2.5 * 1361.0)
    assert req1["limit_value"] == 500.0

    # Check that REQ-002 (Battery usable capacity: 60.0 > 50.0 limit) is satisfied
    req2 = next(r for r in verification if r["requirement_id"] == "REQ-002")
    assert req2["satisfied"] is True
    assert req2["measured_value"] == 60.0
    assert req2["limit_value"] == 50.0

    # Check that REQ-003 (Total Generation: ~952.7 > 800.0 target) is satisfied
    req3 = next(r for r in verification if r["requirement_id"] == "REQ-003")
    assert req3["satisfied"] is True
    assert req3["measured_value"] == pytest.approx(0.28 * 2.5 * 1361.0)
    assert req3["limit_value"] == 800.0

    # 4. Verify compliance signoff log is produced and contains the right status/details
    assert "signoff_log" in result
    signoff = result["signoff_log"]
    assert "SADS MBSE COMPLIANCE REPORT" in signoff
    assert "REQ-001" in signoff
    assert "REQ-002" in signoff
    assert "REQ-003" in signoff


