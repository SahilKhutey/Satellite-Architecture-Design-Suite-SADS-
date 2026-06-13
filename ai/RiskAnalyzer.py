class RiskAnalyzer:
    @staticmethod
    def evaluate_redundancy(components: list) -> dict:
        counts = {}
        for c in components:
            counts[c] = counts.get(c, 0) + 1
        
        spfs = [k for k, v in counts.items() if v == 1]
        risk_level = "HIGH" if len(spfs) > 0 else "LOW"
        
        return {
            "risk_level": risk_level,
            "single_points_of_failure": spfs,
            "recommendation": "Add redundant backup components for: " + ", ".join(spfs) if risk_level == "HIGH" else "System has redundancy. Risk is low."
        }
