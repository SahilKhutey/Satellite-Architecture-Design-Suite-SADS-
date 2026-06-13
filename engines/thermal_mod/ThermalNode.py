# SADS - Thermal Node
from dataclasses import dataclass, field
from typing import List
from .RadiationModel import Surface
from .HeatSourceModel import Heater

@dataclass
class ThermalNode:
    name: str
    mass_kg: float
    specific_heat_j_kg_k: float = 900.0  # Al
    internal_heat_w: float = 0.0
    temperature_k: float = 300.0
    surfaces: List[Surface] = field(default_factory=list)
    heaters: List[Heater] = field(default_factory=list)

    def total_external_heat_w(self, solar_flux: float = 1361.0) -> float:
        return sum(s.absorbed_solar_heat_w(solar_flux) for s in self.surfaces)

    def total_heaters_heat_w(self) -> float:
        return sum(h.output_power_w(self.temperature_k) for h in self.heaters)
