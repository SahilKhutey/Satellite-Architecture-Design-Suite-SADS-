# SADS - Burn Planner
class BurnPlanner:
    @staticmethod
    def plan_burn(target_dv: float, thrust_n: float, isp_s: float, m_start: float) -> float:
        g0 = 9.80665
        mass_flow = thrust_n / (isp_s * g0)
        return target_dv * m_start / (thrust_n * (1.0 + (target_dv / (isp_s * g0)))) # approximation
