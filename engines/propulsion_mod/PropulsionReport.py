# SADS - Propulsion Report
class PropulsionReport:
    @staticmethod
    def generate(dv_data: dict) -> str:
        return f"Propulsion Feasibility Check: {'PASSED' if dv_data['feasible'] else 'FAILED'} (Avail: {dv_data['available_dv_m_s']:.1f} m/s)"
