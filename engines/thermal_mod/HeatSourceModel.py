# SADS - Heat Source Model
from dataclasses import dataclass

@dataclass
class Heater:
    name: str
    max_power_w: float
    target_temp_k: float
    active: bool = True

    def output_power_w(self, current_temp_k: float) -> float:
        if self.active and current_temp_k < self.target_temp_k:
            return self.max_power_w
        return 0.0
