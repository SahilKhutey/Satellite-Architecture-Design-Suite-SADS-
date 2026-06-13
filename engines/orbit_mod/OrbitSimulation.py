# SADS - Orbit Simulation
from .KeplerPropagator import KeplerPropagator

class OrbitSimulation:
    @staticmethod
    def run(alt: float, steps: int) -> list:
        return [KeplerPropagator.propagate(alt, t * 60) for t in range(steps)]
