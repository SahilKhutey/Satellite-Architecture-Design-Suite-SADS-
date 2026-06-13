# SADS - Radiation Model
from dataclasses import dataclass
import math

SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant

@dataclass
class Surface:
    name: str
    area_m2: float
    emissivity: float
    absorptivity: float
    view_factor_sun: float = 0.0
    view_factor_earth: float = 0.0

    def radiated_heat_w(self, temp_k: float) -> float:
        return self.emissivity * SIGMA * self.area_m2 * (temp_k ** 4)

    def absorbed_solar_heat_w(self, solar_flux: float = 1361.0) -> float:
        return self.absorptivity * self.area_m2 * solar_flux * self.view_factor_sun
