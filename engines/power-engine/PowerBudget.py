# SADS - Power Budget
from typing import List, Dict, Any
from .SolarPanelModel import SolarArray
from .BatteryModel import Battery
from .LoadAnalyzer import Load

class PowerBudget:
    def __init__(self, solar_arrays: List[SolarArray], batteries: List[Battery], loads: List[Load], eclipse_duration_min: float = 35.0, orbit_period_min: float = 95.0):
        self.solar_arrays = solar_arrays
        self.batteries = batteries
        self.loads = loads
        self.eclipse_duration_min = eclipse_duration_min
        self.orbit_period_min = orbit_period_min

    def total_array_power(self) -> float:
        return sum(arr.instantaneous_power() for arr in self.solar_arrays)

    def average_load(self) -> float:
        return sum(load.average_power() for load in self.loads)

    def usable_battery_capacity(self) -> float:
        return sum(b.usable_capacity() for b in self.batteries)

    def eclipse_energy_required(self) -> float:
        return self.average_load() * (self.eclipse_duration_min / 60.0)

    def battery_margin(self) -> float:
        required = self.eclipse_energy_required()
        if required == 0:
            return float('inf')
        return (self.usable_battery_capacity() - required) / required

    def power_balance(self) -> Dict[str, Any]:
        gen = self.total_array_power()
        avg_load = self.average_load()
        eclipse_req = self.eclipse_energy_required()
        margin = self.battery_margin()
        return {
            "generation_w": gen,
            "average_load_w": avg_load,
            "eclipse_energy_wh": eclipse_req,
            "battery_margin": margin,
            "status": "OK" if gen >= avg_load and margin >= 0 else "MARGINAL"
        }
