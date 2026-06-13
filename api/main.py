"""
SADS - Main REST API
Entry point for web, desktop, and XR clients.
Serves both the backend simulation API and the static web frontend.
"""

import os
import json
import math
import asyncio
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple


from engines.power_engine import PowerBudget, SolarArray, Battery, Load
from engines.thermal_engine import ThermalBudget, ThermalNode, Surface, Heater
from engines.propulsion_engine import PropulsionSystem, Thruster, PropellantTank, MissionManeuver
from engines.comm_engine import LinkBudget, Antenna, Transmitter, Receiver
from engines.adcs_engine import ADCSConfig, InertiaTensor, ReactionWheel, Sensor, Actuator
from engines.orbit_engine import OrbitalElements, circular_orbit, hohmann_transfer
from services.simulation_service import MissionTimeline, MissionPhase
from engines.structures_engine import StructuresEngine, StructuralComponent
from engines.payload_engine import PayloadSystem, PayloadComponent



app = FastAPI(
    title="Satellite Architecture Design Suite API",
    version="1.0.0",
    description="Professional aerospace systems engineering platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve directories relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_PATH = os.path.join(BASE_DIR, "data", "component_library.json")
CLIENT_DIR = os.path.join(BASE_DIR, "apps", "web_client")


# ---------- Request Models ----------
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


class CommRequest(BaseModel):
    tx_power_w: float
    tx_line_loss_db: float
    data_rate_bps: float
    rx_diameter_m: float
    rx_frequency_hz: float
    rx_efficiency: float
    distance_km: float
    system_temp_k: float
    required_cn_db: float
    atmospheric_loss_db: float = 1.0


class ADCSRequest(BaseModel):
    inertia: Dict[str, float]
    wheels: List[Dict[str, Any]]
    sensors: List[Dict[str, Any]]
    pointing_requirement_deg: float = 0.1
    slew_rate_dps: float = 1.0


class ComponentRequest(BaseModel):
    name: str
    mass_kg: float
    com: List[float]


class StructuresRequest(BaseModel):
    components: List[ComponentRequest]
    nodes: Optional[List[Tuple[float, float]]] = None
    elements: Optional[List[Tuple[int, int, float, float]]] = None
    applied_forces: Optional[Dict[int, Tuple[float, float]]] = None
    boundary_conditions: Optional[Dict[int, Tuple[bool, bool]]] = None
    static_g_axial: float = 6.0
    dynamic_g_lateral: float = 2.0
    stiffness_n_m: float = 1e7



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



class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if len(self.active_connections) == 1 and not self._broadcast_task:
            self._broadcast_task = asyncio.create_task(self._telemetry_broadcaster())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if len(self.active_connections) == 0 and self._broadcast_task:
            self._broadcast_task.cancel()
            self._broadcast_task = None

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def _telemetry_broadcaster(self):
        """Simulates real-time telemetry from orbital flight parameters"""
        altitude_km = 400.0
        time_elapsed_s = 0.0
        battery_charge_wh = 60.0
        while True:
            try:
                await asyncio.sleep(1.0)
                time_elapsed_s += 1.0
                
                # Orbit parameters (LEO circular speed: ~7.67 km/s, period ~92.6 min)
                period_s = 92.68 * 60.0
                angle = (time_elapsed_s / period_s) * 2.0 * math.pi
                in_sun = math.cos(angle) > -0.3
                
                # Telemetry variables
                generation_w = 400.0 * (0.8 + 0.2 * math.sin(angle * 2.0)) if in_sun else 0.0
                load_w = 120.0 + 10.0 * math.sin(angle)
                
                delta_e_wh = (generation_w - load_w) * (1.0 / 3600.0)
                battery_charge_wh = max(0.0, min(120.0, battery_charge_wh + delta_e_wh))
                battery_soc = (battery_charge_wh / 120.0) * 100.0
                
                base_temp = 20.0
                temp_c = base_temp + 15.0 * math.cos(angle) + np.random.normal(0, 0.1)
                
                # EKF filtered estimations
                temp_k_measured = temp_c + 273.15
                pointing_error_deg = 0.01 + 0.005 * math.sin(angle)
                
                telemetry_packet = {
                    "timestamp": time_elapsed_s,
                    "in_sun": in_sun,
                    "orbit_parameters": {
                        "altitude_km": altitude_km,
                        "latitude_deg": math.degrees(math.sin(angle)) * 0.8,
                        "longitude_deg": (time_elapsed_s * 0.06) % 360.0 - 180.0
                    },
                    "power_telemetry": {
                        "generation_w": generation_w,
                        "load_w": load_w,
                        "battery_charge_wh": battery_charge_wh,
                        "battery_soc_pct": battery_soc,
                        "battery_margin": (battery_charge_wh - 30.0) / 30.0 if battery_charge_wh > 0 else 0.0
                    },
                    "thermal_telemetry": {
                        "temperature_c": temp_c,
                        "temperature_k": temp_k_measured
                    },
                    "adcs_telemetry": {
                        "pointing_error_deg": pointing_error_deg,
                        "reaction_wheel_speeds_rpm": [
                            1200.0 + 300.0 * math.sin(angle),
                            -800.0 + 200.0 * math.cos(angle),
                            450.0 + 50.0 * math.sin(angle * 3)
                        ]
                    }
                }
                await self.broadcast(telemetry_packet)
            except asyncio.CancelledError:
                break
            except Exception:
                pass


manager = ConnectionManager()


@app.websocket("/api/telemetry/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                config = json.loads(data)
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ---------- API Endpoints ----------
@app.get("/api/status")
def status():
    return {
        "service": "SADS - Satellite Architecture Design Suite",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/power/analyze", "/api/thermal/analyze", "/api/propulsion/analyze",
            "/api/comm/analyze", "/api/adcs/analyze", "/api/orbit/circular",
            "/api/orbit/hohmann", "/api/simulation/run", "/api/components/library"
        ]
    }


@app.post("/api/power/analyze")
def analyze_power(req: PowerRequest):
    budget = PowerBudget(
        solar_arrays=[SolarArray(**a) for a in req.arrays],
        batteries=[Battery(**b) for b in req.batteries],
        loads=[Load(**l) for l in req.loads],
        eclipse_duration_min=req.eclipse_duration_min,
        orbit_period_min=req.orbit_period_min,
    )
    return budget.power_balance()


@app.post("/api/thermal/analyze")
def analyze_thermal(req: ThermalRequest):
    nodes = []
    for n in req.nodes:
        surfaces = [Surface(**s) for s in n.get("surfaces", [])]
        heaters = [Heater(**h) for h in n.get("heaters", [])]
        node = ThermalNode(
            name=n["name"],
            mass_kg=n["mass_kg"],
            specific_heat_j_kg_k=n.get("specific_heat_j_kg_k", 900.0),
            internal_heat_w=n.get("internal_heat_w", 0.0),
            temperature_k=n.get("temperature_k", 300.0),
            surfaces=surfaces,
            heaters=heaters,
        )
        nodes.append(node)
    tb = ThermalBudget(nodes=nodes)
    return tb.report()


@app.post("/api/propulsion/analyze")
def analyze_propulsion(req: PropulsionRequest):
    sys = PropulsionSystem(
        thrusters=[Thruster(**t) for t in req.thrusters],
        tanks=[PropellantTank(**tk) for tk in req.tanks],
        dry_mass_kg=req.dry_mass_kg,
        maneuvers=[MissionManeuver(**m) for m in req.maneuvers],
    )
    return sys.report()


@app.post("/api/comm/analyze")
def analyze_comm(req: CommRequest):
    ant = Antenna(name="Receiver Antenna", diameter_m=req.rx_diameter_m, frequency_hz=req.rx_frequency_hz, efficiency=req.rx_efficiency)
    tx = Transmitter(name="Transmitter", power_w=req.tx_power_w, line_loss_db=req.tx_line_loss_db, data_rate_bps=req.data_rate_bps)
    rx = Receiver(name="Receiver", system_temp_k=req.system_temp_k, required_cn_db=req.required_cn_db)
    link = LinkBudget(tx=tx, rx_antenna=ant, receiver=rx, distance_km=req.distance_km,
                      atmospheric_loss_db=req.atmospheric_loss_db)
    return link.compute()


@app.post("/api/adcs/analyze")
def analyze_adcs(req: ADCSRequest):
    inertia = InertiaTensor(**req.inertia)
    config = ADCSConfig(
        inertia=inertia,
        wheels=[ReactionWheel(**w) for w in req.wheels],
        sensors=[Sensor(**s) for s in req.sensors],
        pointing_requirement_deg=req.pointing_requirement_deg,
        slew_rate_dps=req.slew_rate_dps,
    )
    return {
        "pointing": config.pointing_budget(),
        "momentum": config.momentum_management_check(),
        "slew_torque_nm": config.slew_torque_requirement(),
    }


@app.post("/api/orbit/circular")
def orbit_circular(req: OrbitRequest):
    orb = circular_orbit(req.altitude_km, req.inclination_deg)
    orb.eccentricity = req.eccentricity
    return orb.report()


@app.post("/api/orbit/hohmann")
def orbit_hohmann(r1_km: float, r2_km: float):
    return hohmann_transfer(r1_km, r2_km)


@app.post("/api/simulation/run")
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


@app.post("/api/payload/analyze")
def analyze_payload(req: PayloadRequest):
    try:
        payloads = [PayloadComponent(**p) for p in req.payloads]
        sys = PayloadSystem(payloads=payloads, buffer_capacity_bits=req.buffer_capacity_bits)
        sim_res = sys.simulate_step(dt_s=req.duration_s, downlink_rate_bps=req.downlink_rate_bps)
        return {
            "report": sys.report(),
            "simulation": sim_res
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/structures/analyze")
def analyze_structures(req: StructuresRequest):
    components = [StructuralComponent(name=c.name, mass_kg=c.mass_kg, position_m=c.com) for c in req.components]
    engine = StructuresEngine(
        components=components,
        nodes=req.nodes,
        elements=req.elements,
        applied_forces=req.applied_forces,
        boundary_conditions=req.boundary_conditions,
        static_g_axial=req.static_g_axial,
        stiffness_n_m=req.stiffness_n_m
    )
    return engine.report()


@app.post("/api/mbse/cosimulate")
def run_mbse_cosimulate(req: Dict[str, Any]):
    try:
        from mbse.CoSimulation import SysMLCoSimulator
        sysml_blocks_json = req.get("sysml_blocks_json")
        if not sysml_blocks_json:
            if "blocks" in req:
                sysml_blocks_json = json.dumps(req)
            else:
                raise HTTPException(status_code=400, detail="Missing sysml_blocks_json or blocks in request body")
        
        altitude_km = float(req.get("altitude_km", 400.0))
        result = SysMLCoSimulator.run_sysml_co_simulation(sysml_blocks_json, altitude_km=altitude_km)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/components/library")
def components_library():
    try:
        with open(LIBRARY_PATH) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load component library: {str(e)}")


@app.get("/api/structures/subsystem")
def structures_subsystem():
    path = os.path.join(BASE_DIR, "data", "structures_subsystem.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load structures subsystem: {str(e)}")


# ---------- Serve Web Frontend ----------
# We check if CLIENT_DIR exists, then mount it at "/"
if os.path.exists(CLIENT_DIR):
    app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="web_client")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
