# SADS - Interface Definitions
from dataclasses import dataclass

@dataclass
class Port:
    name: str
    port_type: str  # "input" | "output"
    flow_type: str  # "power" | "data" | "thermal" | "fluid"
    capacity: float
