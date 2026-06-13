import json
import pytest
from fastapi.testclient import TestClient
from api.main import app

def test_telemetry_websocket():
    client = TestClient(app)
    
    # Establish a websocket connection
    with client.websocket_connect("/api/telemetry/ws") as websocket:
        # Receive the first telemetry frame broadcasted by the background simulation
        data = websocket.receive_json()
        
        # Verify structure of telemetry packet
        assert "timestamp" in data
        assert "orbit_parameters" in data
        assert "power_telemetry" in data
        assert "thermal_telemetry" in data
        assert "adcs_telemetry" in data
        
        # Verify specific details of the packet
        assert data["orbit_parameters"]["altitude_km"] == 408.0 or data["orbit_parameters"]["altitude_km"] == 400.0
        assert "generation_w" in data["power_telemetry"]
        assert "temperature_c" in data["thermal_telemetry"]
        assert "pointing_error_deg" in data["adcs_telemetry"]
        
        # Send a config message to verify bidirectional support
        websocket.send_text(json.dumps({"command": "status_check"}))
