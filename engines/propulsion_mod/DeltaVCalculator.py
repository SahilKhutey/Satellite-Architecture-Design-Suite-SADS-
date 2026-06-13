# SADS - Delta-V Calculator
import math

class DeltaVCalculator:
    @staticmethod
    def compute_dv(isp_s: float, m_dry: float, m_fuel: float) -> float:
        g0 = 9.80665
        return isp_s * g0 * math.log((m_dry + m_fuel) / m_dry)
