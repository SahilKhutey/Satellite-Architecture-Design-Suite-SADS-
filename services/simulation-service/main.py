# SADS Simulation Service
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Enable importing from root engines folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engines.power_engine import PowerBudget, SolarArray, Battery, Load
from engines.thermal_engine import ThermalBudget, ThermalNode, Surface, Heater
from engines.propulsion_engine import PropulsionSystem, Thruster, PropellantTank, MissionManeuver
from engines.orbit_engine import circular_orbit
from services.simulation_service import MissionTimeline, MissionPhase
from engines.payload_engine import PayloadSystem, PayloadComponent


app = FastAPI(title="SADS Simulation Service", version="1.0.0")

class PowerRequest(BaseModel):
    arrays: List[Dict[str, Any]]
    batteries: List[Dict[str, Any]]
    loads: List[Dict[str, Any]]
    eclipse_duration_min: float = 35.0
    orbit_period_min: float = 95.0

class ThermalRequest(BaseModel):
    nodes: List[Dict[str, Any]]

class PropulsionRequest(BaseModel):
    thrusters: List[Dict[str, Any]]
    tanks: List[Dict[str, Any]]
    dry_mass_kg: float
    maneuvers: List[Dict[str, Any]]

class OrbitRequest(BaseModel):
    altitude_km: float
    inclination_deg: float = 51.6
    eccentricity: float = 0.0

class PayloadRequest(BaseModel):
    payloads: List[Dict[str, Any]]
    buffer_capacity_bits: float = 1e10
    downlink_rate_bps: float = 0.0
    duration_s: float = 60.0

class SimulationRequest(BaseModel):
    satellite_name: str
    phases: List[Dict[str, Any]]
    power: Optional[PowerRequest] = None
    thermal: Optional[ThermalRequest] = None
    propulsion: Optional[PropulsionRequest] = None
    orbit: Optional[OrbitRequest] = None
    payload: Optional[PayloadRequest] = None


@app.get("/status")
def status():
    return {"service": "simulation-service", "status": "active"}

@app.post("/run")
def run_simulation(req: SimulationRequest):
    timeline = MissionTimeline(satellite_name=req.satellite_name)
    timeline.phases = [MissionPhase(**p) for p in req.phases]

    if req.power:
        timeline.power_budget = PowerBudget(
            solar_arrays=[SolarArray(**a) for a in req.power.arrays],
            batteries=[Battery(**b) for b in req.power.batteries],
            loads=[Load(**l) for l in req.power.loads],
            eclipse_duration_min=req.power.eclipse_duration_min,
            orbit_period_min=req.power.orbit_period_min,
        )
    if req.thermal:
        nodes = []
        for n in req.thermal.nodes:
            nodes.append(ThermalNode(
                name=n["name"], mass_kg=n["mass_kg"],
                internal_heat_w=n.get("internal_heat_w", 0.0),
                temperature_k=n.get("temperature_k", 300.0),
                surfaces=[Surface(**s) for s in n.get("surfaces", [])],
                heaters=[Heater(**h) for h in n.get("heaters", [])],
            ))
        timeline.thermal_budget = ThermalBudget(nodes=nodes)
    if req.propulsion:
        timeline.propulsion = PropulsionSystem(
            thrusters=[Thruster(**t) for t in req.propulsion.thrusters],
            tanks=[PropellantTank(**tk) for tk in req.propulsion.tanks],
            dry_mass_kg=req.propulsion.dry_mass_kg,
            maneuvers=[MissionManeuver(**m) for m in req.propulsion.maneuvers],
        )
    if req.orbit:
        timeline.orbit = circular_orbit(req.orbit.altitude_km, req.orbit.inclination_deg)
        timeline.orbit.eccentricity = req.orbit.eccentricity
    if req.payload:
        timeline.payload_system = PayloadSystem(
            payloads=[PayloadComponent(**p) for p in req.payload.payloads],
            buffer_capacity_bits=req.payload.buffer_capacity_bits
        )

    return timeline.simulate()
