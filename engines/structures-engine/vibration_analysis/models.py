# SADS Structures - Vibration Analysis Model
import math

class VibrationAnalysis:
    @staticmethod
    def calculate_natural_frequency_hz(stiffness_n_m: float, mass_kg: float) -> float:
        if mass_kg <= 0 or stiffness_n_m <= 0:
            return 0.0
        return (1.0 / (2.0 * math.pi)) * math.sqrt(stiffness_n_m / mass_kg)

    @staticmethod
    def audit_frequency_compliance(freq_hz: float, requirement_min_hz: float) -> dict:
        passed = freq_hz >= requirement_min_hz
        margin = (freq_hz - requirement_min_hz) / requirement_min_hz if requirement_min_hz > 0 else 0.0
        return {
            "natural_frequency_hz": freq_hz,
            "required_min_hz": requirement_min_hz,
            "margin": margin,
            "status": "PASSED" if passed else "FAILED"
        }
