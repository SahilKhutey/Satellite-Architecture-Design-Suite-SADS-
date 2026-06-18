from fastapi.testclient import TestClient
from api.main import app

def test_orbit_propagate_endpoint():
    client = TestClient(app)
    payload = {
        "altitude_km": 400.0,
        "inclination_deg": 51.6,
        "eccentricity": 0.0,
        "mass_kg": 150.0,
        "drag_area_m2": 2.0,
        "drag_coefficient_cd": 2.2,
        "num_orbits": 0.2, # short run for testing
        "use_perturbations": True
    }
    
    response = client.post("/api/orbit/propagate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "history" in data
    assert "report" in data
    assert len(data["history"]) > 0
    
    rep = data["report"]
    assert "decay_rate_m_day" in rep
    assert "j2_nodal_drift_deg_day" in rep
    assert "final_altitude_km" in rep
    assert rep["final_altitude_km"] <= 400.0


def test_thermal_transient_endpoint():
    client = TestClient(app)
    payload = {
        "length_m": 2.0,
        "thermal_diffusivity": 6.87e-5,
        "init_temp_k": 293.0,
        "boundary_left_k": 300.0,
        "boundary_right_k": 250.0,
        "nodes": 10,
        "time_steps": 10,
        "dt": 1.0
    }
    
    response = client.post("/api/thermal/transient", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "x_coords" in data
    assert "time_steps" in data
    assert "temperatures" in data
    
    assert len(data["x_coords"]) == 10
    assert len(data["time_steps"]) == 11
    assert len(data["temperatures"]) == 11
    assert len(data["temperatures"][0]) == 10


def test_monte_carlo_endpoint():
    client = TestClient(app)
    
    payload = {
        "runs": 20,
        "solar_array_eff_var": 5.0,
        "req": {
            "satellite_name": "TestSat-2",
            "phases": [
                { "name": "Normal Ops", "duration_days": 1.0, "power_load_w": 40.0, "thermal_load_w": 30.0 }
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
            }
        }
    }
    
    response = client.post("/api/reliability/monte-carlo", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "reliability_percent" in data
    assert "statistics" in data
    assert "margins_distribution" in data
    
    stats = data["statistics"]
    assert "mean" in stats
    assert "std" in stats
    assert len(data["margins_distribution"]) == 20
