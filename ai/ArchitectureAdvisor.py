# SADS - Architecture Advisor Agent
class ArchitectureAdvisor:
    @staticmethod
    def analyze_margins(power_margin: float, thermal_margin_k: float, pointing_error_deg: float) -> list:
        recommendations = []
        if power_margin < 0.20:
            recommendations.append("Increase solar panel area or battery capacity. Power margin is below 20% standard limit.")
        if thermal_margin_k < 10.0:
            recommendations.append("Increase radiator surface area or add heater nodes. Thermal safety margin is low.")
        if pointing_error_deg > 0.1:
            recommendations.append("Use star trackers with higher accuracy or add additional reaction wheels.")
        return recommendations
