"""
SADS - Propulsion Subsystem Engine
Tsiolkovsky rocket equation, fuel budgets, thrust calculations.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


G0 = 9.80665  # m/s^2


@dataclass
class Thruster:
    name: str
    isp_s: float  # specific impulse seconds
    thrust_n: float
    mass_kg: float = 0.0
    prop_type: str = "monopropellant"
    pulse_mode: bool = False

    def exhaust_velocity(self) -> float:
        return self.isp_s * G0


@dataclass
class PropellantTank:
    name: str
    mass_kg: float = 0.0
    volume_l: float = 0.0
    density_kg_l: float = 1.0  # hydrazine ~1.0, hydrazine-like


@dataclass
class MissionManeuver:
    name: str
    delta_v_m_s: float


@dataclass
class PropulsionSystem:
    thrusters: List[Thruster] = field(default_factory=list)
    tanks: List[PropellantTank] = field(default_factory=list)
    dry_mass_kg: float = 0.0
    maneuvers: List[MissionManeuver] = field(default_factory=list)

    def total_delta_v(self) -> float:
        return sum(m.delta_v_m_s for m in self.maneuvers)

    def average_isp(self) -> float:
        # weighted by thrust (proxy for authority)
        total_thrust = sum(t.thrust_n for t in self.thrusters)
        if total_thrust == 0:
            return 0.0
        return sum(t.isp_s * t.thrust_n for t in self.thrusters) / total_thrust

    def propellant_mass(self) -> float:
        """Tsiolkovsky: m_p = m0 * (1 - exp(-dv / (Isp*g0)))"""
        m0 = self.dry_mass_kg + self.total_propellant_available()
        isp = self.average_isp()
        if isp == 0 or m0 == 0:
            return 0.0
        dv = self.total_delta_v()
        ve = isp * G0
        m_final = m0 * math.exp(-dv / ve)
        return m0 - m_final

    def total_propellant_available(self) -> float:
        return sum(t.mass_kg for t in self.tanks)

    def fuel_margin(self) -> float:
        req = self.propellant_mass()
        avail = self.total_propellant_available()
        if req == 0:
            return float('inf')
        return (avail - req) / req

    def burn_time(self) -> float:
        isp = self.average_isp()
        m_p = self.propellant_mass()
        if isp == 0:
            return 0.0
        ve = isp * G0
        total_thrust = sum(t.thrust_n for t in self.thrusters)
        mdot = total_thrust / ve
        if mdot == 0:
            return 0.0
        return m_p / mdot

    def report(self) -> Dict[str, float]:
        return {
            "total_delta_v_m_s": self.total_delta_v(),
            "average_isp_s": self.average_isp(),
            "required_propellant_kg": self.propellant_mass(),
            "available_propellant_kg": self.total_propellant_available(),
            "fuel_margin": self.fuel_margin(),
            "burn_time_s": self.burn_time(),
            "dry_mass_kg": self.dry_mass_kg,
            "wet_mass_kg": self.dry_mass_kg + self.total_propellant_available(),
        }


def rocket_equation(dv: float, isp: float, dry_mass: float) -> Dict[str, float]:
    """Compute wet mass and propellant for given dV, Isp, dry mass."""
    ve = isp * G0
    m_final = dry_mass * math.exp(dv / ve)
    m_p = m_final - dry_mass
    return {
        "final_mass_kg": m_final,
        "propellant_mass_kg": m_p,
        "mass_fraction": m_p / m_final if m_final else 0.0
    }
