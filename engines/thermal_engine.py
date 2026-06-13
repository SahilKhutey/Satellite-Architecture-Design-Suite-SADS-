"""
SADS - Thermal Subsystem Engine
Stefan-Boltzmann radiation, conduction, and orbital thermal balance.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


STEFAN_BOLTZMANN = 5.670374419e-8  # W/m^2/K^4


@dataclass
class Surface:
    name: str
    area_m2: float
    absorptivity: float = 0.30
    emissivity: float = 0.85
    view_factor: float = 1.0
    temperature_k: float = 300.0


@dataclass
class Heater:
    name: str
    power_w: float
    duty_cycle: float = 1.0


@dataclass
class ThermalNode:
    """Lumped thermal mass."""
    name: str
    mass_kg: float
    specific_heat_j_kg_k: float = 900.0  # typical aluminum
    internal_heat_w: float = 0.0  # dissipation
    temperature_k: float = 300.0
    surfaces: List[Surface] = field(default_factory=list)
    heaters: List[Heater] = field(default_factory=list)

    def thermal_capacity(self) -> float:
        return self.mass_kg * self.specific_heat_j_kg_k


@dataclass
class ThermalBudget:
    nodes: List[ThermalNode] = field(default_factory=list)
    solar_flux: float = 1361.0
    earth_ir_flux: float = 237.0
    albedo: float = 0.3
    sun_view_factor: float = 0.5
    earth_view_factor: float = 0.3

    def heat_in(self, node: ThermalNode) -> float:
        """Q_in = absorbed solar + albedo + Earth IR + internal dissipation."""
        absorbed_solar = 0.0
        for s in node.surfaces:
            absorbed_solar += s.absorptivity * self.solar_flux * s.area_m2 * self.sun_view_factor
        albedo_in = self.albedo * self.solar_flux * self.earth_view_factor * sum(s.area_m2 for s in node.surfaces) * 0.5
        ir_in = self.earth_ir_flux * self.earth_view_factor * sum(s.area_m2 for s in node.surfaces) * 0.5
        internal = node.internal_heat_w
        return absorbed_solar + albedo_in + ir_in + internal

    def heat_out(self, node: ThermalNode) -> float:
        """Q_out = Stefan-Boltzmann radiation."""
        total = 0.0
        for s in node.surfaces:
            q = s.emissivity * STEFAN_BOLTZMANN * s.area_m2 * (node.temperature_k ** 4) * s.view_factor
            total += q
        return total

    def steady_state_temp(self, node: ThermalNode, iterations: int = 100) -> float:
        """Iteratively solve for equilibrium temperature using the central Newton-Raphson solver."""
        from scientific.numerical_methods.solvers import newton_raphson
        import numpy as np

        def residual(T_arr: np.ndarray) -> np.ndarray:
            T = T_arr[0]
            original_T = node.temperature_k
            node.temperature_k = T
            q_in = self.heat_in(node)
            q_out = self.heat_out(node)
            node.temperature_k = original_T
            return np.array([q_out - q_in])

        def jacobian(T_arr: np.ndarray) -> np.ndarray:
            T = T_arr[0]
            dq_out_dT = 4 * sum(
                s.emissivity * STEFAN_BOLTZMANN * s.area_m2 * (T ** 3) * s.view_factor
                for s in node.surfaces
            )
            return np.array([[dq_out_dT]])

        x0 = np.array([node.temperature_k])
        T_eq_arr = newton_raphson(residual, x0, jac=jacobian, tol=1e-6, max_iter=iterations)
        T_eq = max(50.0, min(400.0, float(T_eq_arr[0])))
        node.temperature_k = T_eq
        return T_eq


    def report(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for node in self.nodes:
            t_eq = self.steady_state_temp(node)
            heater_power = sum(h.power_w * h.duty_cycle for h in node.heaters)
            result[node.name] = {
                "temperature_k": t_eq,
                "temperature_c": t_eq - 273.15,
                "heat_in_w": self.heat_in(node),
                "heat_out_w": self.heat_out(node),
                "heater_power_w": heater_power,
                "margin_ok": 263.15 <= t_eq <= 323.15,  # -10 to +50 C
            }
        return result


def conduction_heat_flow(k: float, area_m2: float, dT: float, thickness_m: float) -> float:
    """Fourier conduction: Q = k*A*dT/L"""
    return k * area_m2 * dT / thickness_m
