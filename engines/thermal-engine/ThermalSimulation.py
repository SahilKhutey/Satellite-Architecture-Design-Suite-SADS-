# SADS - Thermal Simulation
from typing import List
from .ThermalNetwork import ThermalNetwork
from .ThermalSolver import ThermalSolver

class ThermalSimulation:
    def __init__(self, network: ThermalNetwork):
        self.network = network

    def simulate_timeline(self, time_steps_sec: List[float]) -> List[dict]:
        history = []
        for dt in time_steps_sec:
            # We solve equilibrium at each step for simple analytics
            ThermalSolver.solve_equilibrium(self.network)
            history.append({n.name: n.temperature_k for n in self.network.nodes})
        return history
