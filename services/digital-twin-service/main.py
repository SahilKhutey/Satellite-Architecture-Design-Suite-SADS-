# SADS Digital Twin Service
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np

# Enable importing from root scientific and engines folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scientific.state_estimation.ekf_estimator import ExtendedKalmanFilter

app = FastAPI(title="SADS Digital Twin Service", version="1.0.0")

# In-memory store for the current active digital twin state
# State vector: [temperature_k, battery_charge_wh, pointing_error_deg]
x0 = np.array([300.0, 50.0, 0.01])
P0 = np.eye(3) * 1.0
Q = np.eye(3) * 0.1
R = np.eye(3) * 0.05
ekf = ExtendedKalmanFilter(x0, P0, Q, R)

class TelemetryPacket(BaseModel):
    sensor_temp_k: float
    sensor_voltage_v: float
    sensor_current_a: float
    sensor_pointing_deg: float
    dt_seconds: float = 1.0

class FailurePredictionRequest(BaseModel):
    discharge_cycles: int
    operating_temp_c: float
    initial_capacity_wh: float = 100.0

@app.get("/status")
def status():
    return {
        "service": "digital-twin-service",
        "status": "active",
        "state": {
            "temperature_k": float(ekf.x[0]),
            "battery_charge_wh": float(ekf.x[1]),
            "pointing_error_deg": float(ekf.x[2])
        }
    }

@app.post("/api/twin/telemetry")
def telemetry_sync(packet: TelemetryPacket):
    """
    Sync digital twin state with physical telemetry using EKF
    """
    # 1. State transition function f(x) (identity for simplicity over dt)
    def f(x):
        return x
    
    def F_jac(x):
        return np.eye(3)
        
    # Predict step
    ekf.predict(f, F_jac)
    
    # 2. Measurement vector mapping
    z_temp = packet.sensor_temp_k
    z_charge = max(0.0, packet.sensor_voltage_v * packet.sensor_current_a * (packet.dt_seconds / 3600.0) + ekf.x[1])
    z_pointing = packet.sensor_pointing_deg
    z = np.array([z_temp, z_charge, z_pointing])
    
    def h(x):
        return x
        
    def H_jac(x):
        return np.eye(3)
        
    # Update step
    filtered_state = ekf.update(z, h, H_jac)
    
    return {
        "filtered_state": {
            "temperature_k": float(filtered_state[0]),
            "battery_charge_wh": float(filtered_state[1]),
            "pointing_error_deg": float(filtered_state[2])
        },
        "raw_telemetry": {
            "temp_k": z_temp,
            "charge_wh": z_charge,
            "pointing_deg": z_pointing
        }
    }

@app.post("/api/twin/predict-failure")
def predict_failure(req: FailurePredictionRequest):
    """
    Predict component failure using empirical degradation models.
    """
    # Lithium-ion degradation model: capacity loss vs cycles & temp
    temp_factor = 1.0 + max(0.0, req.operating_temp_c - 20.0) * 0.02
    capacity_degradation = req.discharge_cycles * 0.0002 * temp_factor
    remaining_capacity = max(0.0, req.initial_capacity_wh * (1.0 - capacity_degradation))
    
    # Check if capacity is below EOL/DOD safety limit (70% of initial capacity)
    failure_risk = remaining_capacity < (req.initial_capacity_wh * 0.70)
    
    return {
        "cycles": req.discharge_cycles,
        "operating_temp_c": req.operating_temp_c,
        "degradation_percent": capacity_degradation * 100.0,
        "remaining_capacity_wh": remaining_capacity,
        "eol_warning": failure_risk,
        "health_status": "CRITICAL" if failure_risk else "HEALTHY"
    }
