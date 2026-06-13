# SADS - Conduction Model
from dataclasses import dataclass

@dataclass
class ConductiveLink:
    node_a_id: str
    node_b_id: str
    conductivity_w_k: float  # W/K

    def heat_flow_w(self, temp_a_k: float, temp_b_k: float) -> float:
        return self.conductivity_w_k * (temp_a_k - temp_b_k)
