# SADS Structures - Stress Analysis Model
import math

class StressAnalysisSolver:
    @staticmethod
    def calculate_von_mises_stress_mpa(axial_stress_mpa: float, shear_stress_mpa: float) -> float:
        return math.sqrt(axial_stress_mpa**2 + 3.0 * shear_stress_mpa**2)

    @staticmethod
    def factor_of_safety(yield_strength_mpa: float, applied_stress_mpa: float) -> float:
        if applied_stress_mpa <= 0:
            return float('inf')
        return yield_strength_mpa / applied_stress_mpa
