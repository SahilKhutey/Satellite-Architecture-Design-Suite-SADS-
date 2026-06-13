# SADS - Optimization Agent
class OptimizationAgent:
    @staticmethod
    def optimize_eps(load_w: float, eclipse_min: float, cost_factor: float = 1.0) -> dict:
        optimal_battery_wh = load_w * (eclipse_min / 60.0) / 0.50  # 50% DOD limit
        optimal_panel_w = load_w * 2.0
        return {
            "battery_wh": optimal_battery_wh,
            "panel_w": optimal_panel_w,
            "estimated_cost_usd": (optimal_battery_wh * 10.0 + optimal_panel_w * 50.0) * cost_factor
        }
