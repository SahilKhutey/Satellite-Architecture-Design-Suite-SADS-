# SADS - Power Report
from .PowerBudget import PowerBudget

class PowerReport:
    @staticmethod
    def generate(budget: PowerBudget) -> str:
        bal = budget.power_balance()
        return f"""
Power Subsystem Analysis Report
==============================
Solar Array Output: {bal['generation_w']:.2f} W
Nominal Load:       {bal['average_load_w']:.2f} W
Eclipse Energy Req: {bal['eclipse_energy_wh']:.2f} Wh
Battery Margin:     {bal['battery_margin']*100:.1f} %
Status:             {bal['status']}
"""
