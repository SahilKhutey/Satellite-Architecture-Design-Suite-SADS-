import json
from fastapi.testclient import TestClient
from api.main import app

def test_api_cosimulate_endpoint():
    client = TestClient(app)
    
    sysml_blocks = {
        "blocks": [
            {
                "name": "SolarArrayBlock",
                "type": "SolarArray",
                "properties": {
                    "area_m2": 2.0,
                    "efficiency": 0.30
                },
                "requirements": [
                    {
                        "id": "REQ-001",
                        "name": "Solar Array Power Generation Limit",
                        "category": "power",
                        "limit_value": 400.0,
                        "operator": "greater_than"
                    }
                ]
            },
            {
                "name": "BatteryBlock",
                "type": "Battery",
                "properties": {
                    "capacity_wh": 100.0,
                    "dod_limit": 0.50
                },
                "requirements": [
                    {
                        "id": "REQ-002",
                        "name": "Battery Usable Capacity Limit",
                        "category": "power",
                        "limit_value": 40.0,
                        "operator": "greater_than"
                    }
                ]
            },
            {
                "name": "LoadBlock",
                "type": "Load",
                "properties": {
                    "power_draw_w": 20.0
                }
            }
        ]
    }

    # Test passing blocks directly in root
    response = client.post("/api/mbse/cosimulate", json=sysml_blocks)
    assert response.status_code == 200
    data = response.json()
    assert "orbit_parameters" in data
    assert "solver_report" in data
    assert "verification_results" in data
    assert "signoff_log" in data

    # Test passing blocks inside sysml_blocks_json
    payload = {
        "sysml_blocks_json": json.dumps(sysml_blocks),
        "altitude_km": 600.0
    }
    response_json_str = client.post("/api/mbse/cosimulate", json=payload)
    assert response_json_str.status_code == 200
    data_json_str = response_json_str.json()
    assert data_json_str["orbit_parameters"]["altitude_km"] == 600.0
