import os
import json
import pytest
from fastapi.testclient import TestClient
from api.main import app, BASE_DIR, LIBRARY_PATH

def test_schematic_design_crud_flow():
    client = TestClient(app)
    test_design_name = "test-schematic-999"
    
    # 1. Ensure clean starting state: list designs and verify test schematic is not present or clean it up
    response = client.get("/api/design/list")
    assert response.status_code == 200
    designs = response.json().get("designs", [])
    if test_design_name in designs:
        client.delete(f"/api/design/delete/{test_design_name}")

    # 2. Save design
    design_payload = {
        "satellite_name": test_design_name,
        "orbit_preset": "leo",
        "canvas_pan_x": 100,
        "canvas_pan_y": -50,
        "canvas_zoom": 1.2,
        "nodes": {
            "node_solar_panel_1": {
                "id": "node_solar_panel_1",
                "type": "solar_panel",
                "name": "GaAs Panel",
                "x": 200.0,
                "y": 150.0,
                "properties": {"area_m2": 2.5, "efficiency": 0.3}
            }
        },
        "links": [
            {"from": "node_solar_panel_1", "to": "node_battery_1"}
        ]
    }
    
    save_resp = client.post("/api/design/save", json=design_payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["status"] == "success"
    
    # 3. List designs and assert it exists
    list_resp = client.get("/api/design/list")
    assert list_resp.status_code == 200
    assert test_design_name in list_resp.json()["designs"]
    
    # 4. Load design and assert correctness
    load_resp = client.get(f"/api/design/load/{test_design_name}")
    assert load_resp.status_code == 200
    loaded_data = load_resp.json()
    assert loaded_data["satellite_name"] == test_design_name
    assert loaded_data["canvas_zoom"] == 1.2
    assert "node_solar_panel_1" in loaded_data["nodes"]
    assert loaded_data["links"][0]["from"] == "node_solar_panel_1"
    
    # 5. Delete design and verify removal
    delete_resp = client.delete(f"/api/design/delete/{test_design_name}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "success"
    
    # Verify it is no longer listed
    list_resp = client.get("/api/design/list")
    assert test_design_name not in list_resp.json()["designs"]

def test_component_library_and_structures_persistence():
    client = TestClient(app)
    
    # Backup original component library and structures subsystem files
    original_library = None
    if os.path.exists(LIBRARY_PATH):
        with open(LIBRARY_PATH) as f:
            original_library = json.load(f)
            
    struct_path = os.path.join(BASE_DIR, "data", "structures_subsystem.json")
    original_struct = None
    if os.path.exists(struct_path):
        with open(struct_path) as f:
            original_struct = json.load(f)
            
    try:
        # 1. Modify and save component library
        test_library = {"components": {"solar_panels": [{"name": "Test Panel UTJ", "efficiency": 0.35}]}}
        lib_resp = client.post("/api/components/library", json=test_library)
        assert lib_resp.status_code == 200
        
        # Verify saved state via GET
        get_lib_resp = client.get("/api/components/library")
        assert get_lib_resp.status_code == 200
        assert get_lib_resp.json()["components"]["solar_panels"][0]["name"] == "Test Panel UTJ"
        
        # 2. Modify and save structures subsystem
        test_struct = {"satellite_name": "Test-Struct-Sub", "components": [{"id": "bus", "name": "Bus Body", "mass_kg": 50.0, "com": [0,0,0]}]}
        struct_resp = client.post("/api/structures/subsystem", json=test_struct)
        assert struct_resp.status_code == 200
        
        # Verify saved state via GET
        get_struct_resp = client.get("/api/structures/subsystem")
        assert get_struct_resp.status_code == 200
        assert get_struct_resp.json()["satellite_name"] == "Test-Struct-Sub"
        assert get_struct_resp.json()["components"][0]["mass_kg"] == 50.0
        
    finally:
        # Restore original state of files to prevent side effects
        if original_library is not None:
            with open(LIBRARY_PATH, "w") as f:
                json.dump(original_library, f, indent=2)
        if original_struct is not None:
            with open(struct_path, "w") as f:
                json.dump(original_struct, f, indent=2)
