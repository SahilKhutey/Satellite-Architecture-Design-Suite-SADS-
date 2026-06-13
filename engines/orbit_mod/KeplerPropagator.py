# SADS - Kepler Propagator
import math

class KeplerPropagator:
    @staticmethod
    def propagate(alt_km: float, dt_s: float) -> float:
        r_earth = 6378.137
        mu = 398600.4418
        a = r_earth + alt_km
        n = math.sqrt(mu / a**3)
        return (n * dt_s) % (2 * math.pi)  # Change in anomaly
