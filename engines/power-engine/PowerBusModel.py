# SADS - Power Bus Model
from dataclasses import dataclass

@dataclass
class PowerBus:
    name: str
    voltage_v: float = 28.0
    efficiency: float = 0.98
