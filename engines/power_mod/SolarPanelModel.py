# SADS - Solar Panel Model
from dataclasses import dataclass

@dataclass
class SolarArray:
    name: str
    area: float  # m^2
    efficiency: float = 0.30  # typical triple-junction GaAs
    degradation_per_year: float = 0.025
    cell_type: str = "triple-junction"
    years_in_service: float = 0.0

    def instantaneous_power(self, solar_flux: float = 1361.0) -> float:
        """P = eta * A * G"""
        deg = (1 - self.degradation_per_year) ** self.years_in_service
        return self.efficiency * self.area * solar_flux * deg
