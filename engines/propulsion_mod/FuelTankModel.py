# SADS - Fuel Tank Model
from dataclasses import dataclass

@dataclass
class FuelTank:
    name: str
    fuel_mass_kg: float
    max_capacity_kg: float
