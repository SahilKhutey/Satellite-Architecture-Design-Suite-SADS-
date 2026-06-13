# SADS - Power Simulation
from typing import List
from .PowerBudget import PowerBudget

class PowerSimulation:
    def __init__(self, budget: PowerBudget):
        self.budget = budget

    def run_time_series(self, time_steps_min: List[float]) -> List[float]:
        soc_history = []
        capacity_wh = sum(b.capacity_wh for b in self.budget.batteries)
        usable_wh = self.budget.usable_battery_capacity()
        current_soc_wh = usable_wh

        for t in time_steps_min:
            gen = self.budget.total_array_power()
            load = self.budget.average_load()
            net_power = gen - load
            current_soc_wh = max(0.0, min(capacity_wh, current_soc_wh + net_power * (1.0 / 60.0)))
            soc_history.append((current_soc_wh / capacity_wh) * 100.0 if capacity_wh else 0.0)
        return soc_history
