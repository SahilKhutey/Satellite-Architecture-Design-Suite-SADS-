from fastapi.testclient import TestClient
from api.main import app

def test_optimization_endpoint():
    client = TestClient(app)
    
    # Define a valid SADS design payload representing a satellite EPS design
    payload = {
        "satellite_name": "TestSat-1",
        "phases": [
            { "name": "Sunlight Phase", "duration_days": 0.04, "power_load_w": 120.0, "thermal_load_w": 100.0, "adcs_mode": "sun_pointing" },
            { "name": "Eclipse Phase", "duration_days": 0.02, "power_load_w": 120.0, "thermal_load_w": 60.0, "adcs_mode": "nadir" }
        ],
        "power": {
            "arrays": [
                { "name": "GaAs Panel Array", "area": 1.5, "efficiency": 0.30 }
            ],
            "batteries": [
                { "name": "Li-ion Pack", "capacity_wh": 120.0, "dod_limit": 0.30, "mass_kg": 2.4 }
            ],
            "loads": [
                { "name": "OBC + Comms", "nominal_power_w": 30.0, "duty_cycle": 1.0 }
            ],
            "eclipse_duration_min": 35.0,
            "orbit_period_min": 95.0
        },
        "propulsion": {
            "dry_mass_kg": 45.0,
            "thrusters": [],
            "tanks": [],
            "maneuvers": []
        },
        "orbit": {
            "altitude_km": 400.0,
            "inclination_deg": 51.6
        }
    }
    
    response = client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "variants" in data
    assert "pareto_front" in data
    assert "optimum" in data
    
    # Check that we have the requested 40 variants
    assert len(data["variants"]) == 40
    assert len(data["pareto_front"]) >= 1
    
    # Verify the values of the optimized design points
    opt = data["optimum"]
    assert opt["area_m2"] > 0.0
    assert opt["capacity_wh"] > 0.0
    assert opt["mass_kg"] > 45.0  # Must be greater than dry mass
    assert "power_margin_w" in opt
