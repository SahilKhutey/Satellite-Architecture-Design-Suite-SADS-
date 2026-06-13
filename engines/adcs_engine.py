"""
SADS - ADCS Engine
Rigid body dynamics, reaction wheel sizing, pointing budgets.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


@dataclass
class InertiaTensor:
    ixx: float = 0.0
    iyy: float = 0.0
    izz: float = 0.0
    ixy: float = 0.0
    ixz: float = 0.0
    iyz: float = 0.0


@dataclass
class ReactionWheel:
    name: str
    max_torque_nm: float = 0.01
    max_momentum_nms: float = 0.05
    mass_kg: float = 1.0
    axes: int = 1


@dataclass
class Sensor:
    name: str
    sensor_type: str  # "star_tracker", "sun_sensor", "gyro", "magnetometer"
    accuracy_deg: float = 0.01
    noise_deg: float = 0.005
    update_rate_hz: float = 10.0


@dataclass
class Actuator:
    name: str
    actuator_type: str  # "reaction_wheel", "magnetorquer", "thruster"
    torque_nm: float = 0.0


@dataclass
class ADCSConfig:
    inertia: InertiaTensor
    sensors: List[Sensor] = field(default_factory=list)
    actuators: List[Actuator] = field(default_factory=list)
    wheels: List[ReactionWheel] = field(default_factory=list)
    pointing_requirement_deg: float = 0.1
    slew_rate_dps: float = 1.0

    def total_wheel_momentum_capacity(self) -> float:
        return sum(w.max_momentum_nms for w in self.wheels)

    def slew_torque_requirement(self) -> float:
        """tau = I * alpha"""
        avg_I = (self.inertia.ixx + self.inertia.iyy + self.inertia.izz) / 3.0
        alpha = math.radians(self.slew_rate_dps)
        return avg_I * alpha

    def pointing_budget(self) -> Dict[str, float]:
        # root-sum-square of sensor and actuator contributions
        sensor_err = math.sqrt(sum(s.accuracy_deg ** 2 for s in self.sensors)) if self.sensors else 0.0
        # assume actuator noise ~ 0.01 deg
        actuator_err = 0.01
        total = math.sqrt(sensor_err ** 2 + actuator_err ** 2)
        return {
            "sensor_error_3sigma_deg": sensor_err,
            "actuator_error_3sigma_deg": actuator_err,
            "total_3sigma_deg": total,
            "requirement_deg": self.pointing_requirement_deg,
            "margin_ok": total <= self.pointing_requirement_deg,
        }

    def momentum_management_check(self, disturbance_nms_per_day: float = 0.01) -> Dict[str, float]:
        cap = self.total_wheel_momentum_capacity()
        days_to_saturate = cap / disturbance_nms_per_day if disturbance_nms_per_day else float('inf')
        return {
            "capacity_nms": cap,
            "disturbance_nms_per_day": disturbance_nms_per_day,
            "days_to_saturation": days_to_saturate,
            "acceptable": days_to_saturate > 1.0,
        }


def torque_required(inertia_kgm2: float, angular_accel_rad_s2: float) -> float:
    """tau = I * alpha"""
    return inertia_kgm2 * angular_accel_rad_s2
