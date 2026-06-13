"""
SADS - Mission Simulation Service
End-to-end mission timeline simulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math

from engines.power_engine import PowerBudget
from engines.thermal_engine import ThermalBudget
from engines.propulsion_engine import PropulsionSystem
from engines.orbit_engine import OrbitalElements
from engines.payload_engine import PayloadSystem



@dataclass
class MissionPhase:
    name: str
    duration_days: float
    power_load_w: float
    thermal_load_w: float
    adcs_mode: str = "sun_pointing"  # sun_pointing, nadir, inertial, off


@dataclass
class MissionTimeline:
    satellite_name: str
    phases: List[MissionPhase] = field(default_factory=list)
    power_budget: PowerBudget = None
    thermal_budget: ThermalBudget = None
    propulsion: PropulsionSystem = None
    orbit: OrbitalElements = None
    payload_system: PayloadSystem = None


    def total_duration_days(self) -> float:
        return sum(p.duration_days for p in self.phases)

    def cumulative_energy_wh(self) -> float:
        return sum(p.power_load_w * p.duration_days * 24.0 for p in self.phases)

    def simulate(self) -> Dict:
        power_status = self.power_budget.power_balance() if self.power_budget else {}
        thermal_status = self.thermal_budget.report() if self.thermal_budget else {}
        propulsion_status = self.propulsion.report() if self.propulsion else {}
        orbit_status = self.orbit.report() if self.orbit else {}

        # Simulate payloads if present
        payload_status = {}
        if self.payload_system:
            total_time_s = self.total_duration_days() * 86400.0
            payload_status["simulation"] = self.payload_system.simulate_step(dt_s=total_time_s, downlink_rate_bps=1e6)
            payload_status["report"] = self.payload_system.report()

        return {
            "satellite": self.satellite_name,
            "mission_duration_days": self.total_duration_days(),
            "total_energy_wh": self.cumulative_energy_wh(),
            "power": power_status,
            "thermal": thermal_status,
            "propulsion": propulsion_status,
            "orbit": orbit_status,
            "payload": payload_status,
            "feasibility": {
                "power_ok": power_status.get("status") == "OK" if power_status else True,
                "thermal_ok": all(v.get("margin_ok", True) for v in thermal_status.values()) if thermal_status else True,
                "propulsion_ok": (propulsion_status.get("fuel_margin", 0) >= 0) if propulsion_status and propulsion_status.get("fuel_margin") != float('inf') else True,
                "payload_overflow": payload_status.get("simulation", {}).get("buffer_overflow", False) if payload_status else False,
            }
        }

