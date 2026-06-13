# SADS - Power Validator
from .PowerBudget import PowerBudget

class PowerValidator:
    @staticmethod
    def validate_margins(budget: PowerBudget) -> bool:
        balance = budget.power_balance()
        # Verify 20% margin
        if balance["generation_w"] < balance["average_load_w"] * 1.20:
            return False
        return balance["battery_margin"] >= 0.0
