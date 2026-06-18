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
from scientific.optimization.optimizers import nelder_mead
from engines.orbit_mod.CowellPropagator import CowellPropagator
from scientific.finite_difference.transient_solvers import HeatEquation1DSolver
from scientific.monte_carlo.analysis import MonteCarloAnalysis



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


@app.post("/api/optimization/run")
def run_optimization(req: SimulationRequest):
    # Extract baseline specs from design canvas payload
    if not req.power or not req.power.arrays:
        avg_load = 50.0
        efficiency = 0.28
        dod_limit = 0.30
        eclipse_duration_min = 35.0
        base_mass = 50.0
    else:
        avg_load = sum(l.get("nominal_power_w", 0.0) * l.get("duty_cycle", 1.0) for l in req.power.loads) if req.power.loads else 20.0
        if avg_load == 0:
            avg_load = 20.0
        efficiency = req.power.arrays[0].get("efficiency", 0.30) if req.power.arrays else 0.30
        dod_limit = req.power.batteries[0].get("dod_limit", 0.30) if req.power.batteries else 0.30
        eclipse_duration_min = req.power.eclipse_duration_min
        base_mass = req.propulsion.dry_mass_kg if req.propulsion else 50.0

    # 1. Generate 40 variants in design space around optimal bounds
    min_area = (avg_load + 20.0) / (efficiency * 1361.0)
    min_capacity = (avg_load * (eclipse_duration_min / 60.0)) / dod_limit
    
    variants = []
    np.random.seed(42)
    for _ in range(40):
        # Sample area around min_area
        area = float(min_area + np.random.uniform(-0.2 * min_area, 1.4 * min_area))
        area = max(0.1, area)
        # Sample capacity around min_capacity
        cap = float(min_capacity + np.random.uniform(-0.2 * min_capacity, 1.4 * min_capacity))
        cap = max(10.0, cap)
        
        mass = float(base_mass + area * 2.5 + cap * 0.04)
        margin = float(area * efficiency * 1361.0 - avg_load)
        
        variants.append({
            "mass": mass,
            "margin": margin,
            "area": area,
            "capacity": cap
        })
        
    # 2. Extract the Pareto-optimal front
    pareto_front = []
    for v1 in variants:
        dominated = False
        for v2 in variants:
            if v2["mass"] <= v1["mass"] and v2["margin"] >= v1["margin"]:
                if v2["mass"] < v1["mass"] or v2["margin"] > v1["margin"]:
                    dominated = True
                    break
        if not dominated:
            pareto_front.append(v1)
            
    pareto_front.sort(key=lambda x: x["mass"])
    
    # 3. Solve exact multivariable mathematical optimum via Nelder-Mead
    def cost_function(x):
        area, cap = x[0], x[1]
        if area < 0.1 or cap < 10.0:
            return 1e9
        
        mass = base_mass + area * 2.5 + cap * 0.04
        power_gen = area * efficiency * 1361.0
        usable_cap = cap * dod_limit
        eclipse_req = avg_load * (eclipse_duration_min / 60.0)
        
        penalty = 0.0
        if power_gen < avg_load + 20.0:
            penalty += (avg_load + 20.0 - power_gen) * 500.0
        if usable_cap < eclipse_req:
            penalty += (eclipse_req - usable_cap) * 500.0
            
        return mass + penalty
        
    current_area = req.power.arrays[0].get("area", 1.5) if (req.power and req.power.arrays) else 1.5
    current_cap = req.power.batteries[0].get("capacity_wh", 120.0) if (req.power and req.power.batteries) else 120.0
    x0 = np.array([current_area, current_cap])
    
    opt_x = nelder_mead(cost_function, x0, step=0.1, max_iter=200)
    
    opt_area = float(max(0.1, opt_x[0]))
    opt_cap = float(max(10.0, opt_x[1]))
    opt_mass = float(base_mass + opt_area * 2.5 + opt_cap * 0.04)
    opt_margin = float(opt_area * efficiency * 1361.0 - avg_load)

    # 4. Inject mathematically optimal point on Pareto line
    pareto_front.append({
        "mass": opt_mass,
        "margin": opt_margin,
        "area": opt_area,
        "capacity": opt_cap
    })
    pareto_front.sort(key=lambda x: x["mass"])

    return {
        "status": "success",
        "variants": [{"x": float(v["mass"]), "y": float(v["margin"])} for v in variants],
        "pareto_front": [{"x": float(v["mass"]), "y": float(v["margin"])} for v in pareto_front],
        "optimum": {
            "area_m2": opt_area,
            "capacity_wh": opt_cap,
            "mass_kg": opt_mass,
            "power_margin_w": opt_margin
        }
    }


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


# ---------- Design Schematic & Subsystem Datasets Endpoints ----------
SCHEMATICS_DIR = os.path.join(BASE_DIR, "data", "satellites")

@app.post("/api/design/save")
def save_design(design: Dict[str, Any]):
    name = design.get("satellite_name")
    if not name:
        raise HTTPException(status_code=400, detail="satellite_name is required")
    # Sanitize name
    name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="Invalid satellite name")
    
    os.makedirs(SCHEMATICS_DIR, exist_ok=True)
    path = os.path.join(SCHEMATICS_DIR, f"{name}.json")
    try:
        with open(path, "w") as f:
            json.dump(design, f, indent=2)
        return {"status": "success", "message": f"Design '{name}' saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save design: {str(e)}")

@app.get("/api/design/load/{name}")
def load_design(name: str):
    name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
    path = os.path.join(SCHEMATICS_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Design '{name}' not found")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load design: {str(e)}")

@app.get("/api/design/list")
def list_designs():
    try:
        os.makedirs(SCHEMATICS_DIR, exist_ok=True)
        files = [f[:-5] for f in os.listdir(SCHEMATICS_DIR) if f.endswith(".json")]
        return {"status": "success", "designs": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list designs: {str(e)}")

@app.delete("/api/design/delete/{name}")
def delete_design(name: str):
    name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
    path = os.path.join(SCHEMATICS_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Design '{name}' not found")
    try:
        os.remove(path)
        return {"status": "success", "message": f"Design '{name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete design: {str(e)}")

@app.post("/api/components/library")
def save_components_library(library: Dict[str, Any]):
    try:
        with open(LIBRARY_PATH, "w") as f:
            json.dump(library, f, indent=2)
        return {"status": "success", "message": "Component library saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save component library: {str(e)}")

@app.post("/api/structures/subsystem")
def save_structures_subsystem(data: Dict[str, Any]):
    path = os.path.join(BASE_DIR, "data", "structures_subsystem.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return {"status": "success", "message": "Structures subsystem saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save structures subsystem: {str(e)}")


# ---------- Advanced Solver Request Models ----------
class OrbitPropagationRequest(BaseModel):
    altitude_km: float
    inclination_deg: float = 51.6
    eccentricity: float = 0.0
    mass_kg: float = 150.0
    drag_area_m2: float = 2.0
    drag_coefficient_cd: float = 2.2
    num_orbits: float = 2.0
    use_perturbations: bool = True


class ThermalTransientRequest(BaseModel):
    length_m: float = 2.0
    thermal_diffusivity: float = 6.87e-5
    init_temp_k: float = 293.0
    boundary_left_k: float = 300.0
    boundary_right_k: float = 250.0
    nodes: int = 10
    time_steps: int = 50
    dt: float = 10.0


class MonteCarloRequest(BaseModel):
    runs: int = 100
    solar_array_eff_var: float = 5.0
    req: SimulationRequest


def coe_to_rv(a: float, e: float, i_deg: float, raan_deg: float, arg_pe_deg: float, true_anom_deg: float, mu: float = 398600.4418):
    i = math.radians(i_deg)
    raan = math.radians(raan_deg)
    arg_pe = math.radians(arg_pe_deg)
    ta = math.radians(true_anom_deg)
    
    p = a * (1.0 - e**2)
    denom = (1.0 + e * math.cos(ta))
    r_mag = p / denom if denom != 0 else p
    
    r_pqw = np.array([
        r_mag * math.cos(ta),
        r_mag * math.sin(ta),
        0.0
    ])
    
    sqrt_mu_p = math.sqrt(mu / p) if p > 0 else 0.0
    v_pqw = np.array([
        -sqrt_mu_p * math.sin(ta),
        sqrt_mu_p * (e + math.cos(ta)),
        0.0
    ])
    
    c_raan, s_raan = math.cos(raan), math.sin(raan)
    c_i, s_i = math.cos(i), math.sin(i)
    c_ap, s_ap = math.cos(arg_pe), math.sin(arg_pe)
    
    R = np.zeros((3, 3))
    R[0, 0] = c_raan * c_ap - s_raan * s_ap * c_i
    R[0, 1] = -c_raan * s_ap - s_raan * c_ap * c_i
    R[0, 2] = s_raan * s_i
    
    R[1, 0] = s_raan * c_ap + c_raan * s_ap * c_i
    R[1, 1] = -s_raan * s_ap + c_raan * c_ap * c_i
    R[1, 2] = -c_raan * s_i
    
    R[2, 0] = s_ap * s_i
    R[2, 1] = c_ap * s_i
    R[2, 2] = c_i
    
    r_eci = R @ r_pqw
    v_eci = R @ v_pqw
    return r_eci.tolist(), v_eci.tolist()


@app.post("/api/orbit/propagate")
def orbit_propagate(req: OrbitPropagationRequest):
    try:
        a = (6378.137 + req.altitude_km)
        e = req.eccentricity
        i_deg = req.inclination_deg
        
        r_eci, v_eci = coe_to_rv(a, e, i_deg, 0.0, 0.0, 0.0)
        
        mu = 398600.4418
        period_s = 2 * math.pi * math.sqrt(a ** 3 / mu)
        total_time_s = req.num_orbits * period_s
        
        dt_step = 60.0
        steps_count = int(total_time_s / dt_step)
        if steps_count > 500:
            steps_count = 500
            dt_step = total_time_s / steps_count
            
        history = []
        curr_pos = r_eci
        curr_vel = v_eci
        t = 0.0
        
        for step_idx in range(steps_count + 1):
            r_mag = np.linalg.norm(curr_pos)
            alt_km = r_mag - 6378.137
            
            history.append({
                "time_s": t,
                "position": curr_pos,
                "velocity": curr_vel,
                "altitude_km": alt_km
            })
            
            if step_idx < steps_count:
                curr_pos, curr_vel = CowellPropagator.step(
                    curr_pos, curr_vel, dt_step, mu,
                    mass=req.mass_kg, area=req.drag_area_m2, cd=req.drag_coefficient_cd,
                    use_perturbations=req.use_perturbations
                )
                t += dt_step
                
        initial_alt = history[0]["altitude_km"]
        final_alt = history[-1]["altitude_km"]
        decay_rate_m_day = ((initial_alt - final_alt) * 1000.0) / (total_time_s / 86400.0) if total_time_s > 0 else 0.0
        
        i_rad = math.radians(i_deg)
        n = math.sqrt(mu / a**3)
        p = a * (1 - e**2)
        j2 = 1.08263e-3
        raan_rate_rad_s = -1.5 * n * j2 * (6378.137 / p) ** 2 * math.cos(i_rad) / (1 - e ** 2) ** 2
        j2_drift_deg_day = math.degrees(raan_rate_rad_s) * 86400.0
        
        return {
            "status": "success",
            "history": history,
            "report": {
                "decay_rate_m_day": decay_rate_m_day,
                "j2_nodal_drift_deg_day": j2_drift_deg_day,
                "final_altitude_km": final_alt,
                "orbital_period_min": period_s / 60.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/thermal/transient")
def thermal_transient(req: ThermalTransientRequest):
    try:
        history = HeatEquation1DSolver.solve_transient(
            length_m=req.length_m,
            thermal_diffusivity=req.thermal_diffusivity,
            init_temp_k=req.init_temp_k,
            boundary_temps_k=(req.boundary_left_k, req.boundary_right_k),
            nodes=req.nodes,
            time_steps=req.time_steps,
            dt=req.dt
        )
        
        history_list = history.tolist()
        x_coords = np.linspace(0, req.length_m, req.nodes).tolist()
        time_steps_sec = [i * req.dt for i in range(req.time_steps + 1)]
        
        return {
            "status": "success",
            "x_coords": x_coords,
            "time_steps": time_steps_sec,
            "temperatures": history_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/reliability/monte-carlo")
def reliability_monte_carlo(req: MonteCarloRequest):
    try:
        if not req.req.power or not req.req.power.arrays:
            base_eff = 0.30
            base_load = 50.0
            base_flux = 1361.0
            base_capacity = 200.0
            dod_limit = 0.30
            eclipse_duration_min = 35.0
            orbit_period_min = 95.0
        else:
            p = req.req.power
            base_eff = p.arrays[0].get("efficiency", 0.30) if p.arrays else 0.30
            base_load = sum(l.get("nominal_power_w", 0.0) * l.get("duty_cycle", 1.0) for l in p.loads) if p.loads else 50.0
            base_flux = 1361.0
            base_capacity = sum(b.get("capacity_wh", 0.0) for b in p.batteries) if p.batteries else 200.0
            dod_limit = p.batteries[0].get("dod_limit", 0.30) if p.batteries else 0.30
            eclipse_duration_min = p.eclipse_duration_min
            orbit_period_min = p.orbit_period_min

        eff_std = base_eff * (req.solar_array_eff_var / 100.0)
        
        def model_fn(params):
            eff = params["efficiency"]
            flux = params["solar_flux"]
            load = params["average_load"]
            
            total_area = sum(arr.get("area", 1.0) for arr in req.req.power.arrays) if (req.req.power and req.req.power.arrays) else 2.0
            generation = eff * total_area * flux
            
            eclipse_energy_req = load * (eclipse_duration_min / 60.0)
            usable_capacity = base_capacity * dod_limit
            
            if eclipse_energy_req == 0:
                bat_margin = 10.0
            else:
                bat_margin = (usable_capacity - eclipse_energy_req) / eclipse_energy_req
                
            if generation < load:
                bat_margin = bat_margin - (load - generation) / load
                
            return bat_margin

        base_params = {
            "efficiency": base_eff,
            "solar_flux": base_flux,
            "average_load": base_load
        }
        
        perturbations = {
            "efficiency": (0.0, eff_std),
            "solar_flux": (0.0, 15.0),
            "average_load": (0.0, base_load * 0.05)
        }
        
        results = MonteCarloAnalysis.run_ensemble(
            model_fn=model_fn,
            base_params=base_params,
            perturbations=perturbations,
            samples=req.runs
        )
        
        successes = 0
        margins = []
        for _ in range(req.runs):
            params = {}
            for k, (mean, std) in perturbations.items():
                params[k] = float(base_params[k] + np.random.normal(mean, std))
            params["efficiency"] = max(0.01, min(0.60, params["efficiency"]))
            margin = model_fn(params)
            margins.append(margin)
            if margin >= 0.0:
                successes += 1
                
        reliability_rate = (successes / req.runs) * 100.0
        
        return {
            "status": "success",
            "samples_count": req.runs,
            "reliability_percent": reliability_rate,
            "statistics": results,
            "margins_distribution": margins
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Serve Web Frontend ----------
# We check if CLIENT_DIR exists, then mount it at "/"
if os.path.exists(CLIENT_DIR):
    app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="web_client")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
