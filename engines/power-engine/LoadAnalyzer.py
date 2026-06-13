# SADS - Load Analyzer
from dataclasses import dataclass

@dataclass
class Load:
    name: str
    nominal_power_w: float
    duty_cycle: float = 1.0  # fraction of orbit time active
    bus_voltage: float = 28.0

    def average_power(self) -> float:
        return self.nominal_power_w * self.duty_cycle
