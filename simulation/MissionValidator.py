from typing import List, Dict

class MissionValidator:
    @staticmethod
    def audit_state_history(states: List[Dict[str, float]]) -> List[str]:
        warnings = []
        for idx, s in enumerate(states):
            soc = s.get("battery_soc", 1.0)
            if soc < 0.30:
                warnings.append(f"Step {idx}: Battery SOC fell below 30% DoD limit (value: {soc:.2f})")
            
            temp = s.get("temp_k", 298.15)
            if temp < 253.15 or temp > 333.15:
                warnings.append(f"Step {idx}: Temperature exceeded qualification limits (value: {temp:.2f} K)")
        return warnings
