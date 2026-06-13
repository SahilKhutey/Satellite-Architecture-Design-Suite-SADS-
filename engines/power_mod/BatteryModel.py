# SADS - Battery Model
from dataclasses import dataclass

@dataclass
class Battery:
    name: str
    capacity_wh: float  # Watt-hours
    dod_limit: float = 0.30  # depth of discharge
    efficiency: float = 0.95
    mass_kg: float = 0.0
    cell_type: str = "Li-ion"

    def usable_capacity(self) -> float:
        return self.capacity_wh * self.dod_limit

    def energy_density(self) -> float:
        if self.mass_kg <= 0:
            return 0.0
        return self.capacity_wh / self.mass_kg
