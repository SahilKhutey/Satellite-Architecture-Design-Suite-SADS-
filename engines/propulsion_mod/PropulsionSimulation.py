# SADS - Propulsion Simulation
from .DeltaVCalculator import DeltaVCalculator

class PropulsionSimulation:
    @staticmethod
    def simulate_maneuvers(isp: float, m_dry: float, m_fuel: float, dv_req: float) -> dict:
        avail_dv = DeltaVCalculator.compute_dv(isp, m_dry, m_fuel)
        return {"available_dv_m_s": avail_dv, "feasible": avail_dv >= dv_req}
