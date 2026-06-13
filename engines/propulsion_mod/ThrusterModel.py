# SADS - Thruster Model
from dataclasses import dataclass

@dataclass
class Thruster:
    name: str
    isp_s: float
    thrust_n: float
