# SADS - Eclipse Analyzer
import math

class EclipseAnalyzer:
    @staticmethod
    def calculate_eclipse_duration(altitude_km: float, radius_earth_km: float = 6378.137, mu_earth: float = 398600.4418) -> float:
        r = radius_earth_km + altitude_km
        t_orbit = 2 * math.pi * math.sqrt(r**3 / mu_earth)
        theta = 2 * math.asin(radius_earth_km / r)
        t_eclipse = t_orbit * (theta / (2 * math.pi))
        return t_eclipse / 60.0  # minutes
