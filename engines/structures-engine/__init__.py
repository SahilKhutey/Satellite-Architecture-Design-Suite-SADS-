# SADS Structures Engine Package
from dataclasses import dataclass

@dataclass
class StressAnalysis:
    name: str
    material_yield_strength_mpa: float = 250.0
    applied_stress_mpa: float = 120.0

    def factor_of_safety(self) -> float:
        if self.applied_stress_mpa <= 0:
            return float('inf')
        return self.material_yield_strength_mpa / self.applied_stress_mpa
