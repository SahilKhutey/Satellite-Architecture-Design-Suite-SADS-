# SADS Payload Engine - Core Model
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PayloadComponent:
    name: str
    payload_type: str  # "optical" | "radar" | "communication" | "science"
    mass_kg: float
    nominal_power_w: float
    peak_power_w: float
    data_rate_bps: float
    state: str = "standby"  # "off" | "standby" | "active"

    def get_power_consumption(self) -> float:
        if self.state == "off":
            return 0.0
        elif self.state == "active":
            return self.peak_power_w
        return self.nominal_power_w

    def get_data_generation_rate(self) -> float:
        if self.state == "active":
            return self.data_rate_bps
        return 0.0

class PayloadSystem:
    def __init__(self, payloads: List[PayloadComponent], buffer_capacity_bits: float = 1e10):
        self.payloads = payloads
        self.buffer_capacity_bits = buffer_capacity_bits
        self.buffer_fill_bits = 0.0

    def get_total_mass(self) -> float:
        return sum(p.mass_kg for p in self.payloads)

    def get_current_power_draw(self) -> float:
        return sum(p.get_power_consumption() for p in self.payloads)

    def simulate_step(self, dt_s: float, downlink_rate_bps: float = 0.0) -> Dict[str, Any]:
        """
        Simulate data generation and downlink for a step of dt_s seconds.
        """
        total_gen_rate = sum(p.get_data_generation_rate() for p in self.payloads)
        generated_bits = total_gen_rate * dt_s
        downlinked_bits = downlink_rate_bps * dt_s
        
        self.buffer_fill_bits += generated_bits - downlinked_bits
        self.buffer_fill_bits = max(0.0, min(self.buffer_capacity_bits, self.buffer_fill_bits))
        
        buffer_percent = (self.buffer_fill_bits / self.buffer_capacity_bits) * 100.0 if self.buffer_capacity_bits > 0 else 0.0
        
        return {
            "power_draw_w": self.get_current_power_draw(),
            "data_generated_bits": generated_bits,
            "data_downlinked_bits": downlinked_bits,
            "buffer_fill_bits": self.buffer_fill_bits,
            "buffer_percent": buffer_percent,
            "buffer_overflow": self.buffer_fill_bits >= self.buffer_capacity_bits
        }

    def report(self) -> Dict[str, Any]:
        return {
            "total_mass_kg": self.get_total_mass(),
            "buffer_capacity_bits": self.buffer_capacity_bits,
            "buffer_fill_bits": self.buffer_fill_bits,
            "payloads": [
                {
                    "name": p.name,
                    "type": p.payload_type,
                    "mass_kg": p.mass_kg,
                    "power_draw_w": p.get_power_consumption(),
                    "data_rate_bps": p.get_data_generation_rate(),
                    "state": p.state
                }
                for p in self.payloads
            ]
        }
