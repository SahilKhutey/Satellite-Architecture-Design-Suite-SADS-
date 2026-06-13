"""
SADS - Orbit Engine
Keplerian orbits, classical orbital elements, propagation.
"""

from dataclasses import dataclass
from typing import Tuple
import math


MU_EARTH = 3.986004418e14  # m^3/s^2
R_EARTH = 6378137.0  # m
J2 = 1.08263e-3


@dataclass
class OrbitalElements:
    semi_major_axis_m: float
    eccentricity: float
    inclination_deg: float
    raan_deg: float  # right ascension of ascending node
    arg_periapsis_deg: float
    true_anomaly_deg: float

    def orbital_period_s(self) -> float:
        a = self.semi_major_axis_m
        return 2 * math.pi * math.sqrt(a ** 3 / MU_EARTH)

    def apoapsis_m(self) -> float:
        return self.semi_major_axis_m * (1 + self.eccentricity)

    def periapsis_m(self) -> float:
        return self.semi_major_axis_m * (1 - self.eccentricity)

    def altitude_apoapsis_km(self) -> float:
        return (self.apoapsis_m() - R_EARTH) / 1000.0

    def altitude_periapsis_km(self) -> float:
        return (self.periapsis_m() - R_EARTH) / 1000.0

    def mean_motion_rad_s(self) -> float:
        a = self.semi_major_axis_m
        return math.sqrt(MU_EARTH / a ** 3)

    def velocity_at(self, true_anomaly_deg: float) -> float:
        """Vis-viva: v = sqrt(mu * (2/r - 1/a))"""
        a = self.semi_major_axis_m
        r = self.radius_at(true_anomaly_deg)
        return math.sqrt(MU_EARTH * (2.0 / r - 1.0 / a))

    def radius_at(self, true_anomaly_deg: float) -> float:
        nu = math.radians(true_anomaly_deg)
        a = self.semi_major_axis_m
        e = self.eccentricity
        # avoid division by zero or negative radius if e >= 1
        return a * (1 - e ** 2) / (1 + e * math.cos(nu))

    def to_eci(self, true_anomaly_deg: float = None) -> Tuple[float, float, float]:
        """Return position in ECI frame (simplified, equatorial plane projection)."""
        if true_anomaly_deg is None:
            true_anomaly_deg = self.true_anomaly_deg
        nu = math.radians(true_anomaly_deg)
        r = self.radius_at(true_anomaly_deg)
        # in orbital plane
        x_op = r * math.cos(nu)
        y_op = r * math.sin(nu)
        # rotation by arg_periapsis + raan (simplified)
        omega = math.radians(self.arg_periapsis_deg + self.raan_deg)
        i = math.radians(self.inclination_deg)
        x = x_op * math.cos(omega) - y_op * math.sin(omega) * math.cos(i)
        y = x_op * math.sin(omega) + y_op * math.cos(omega) * math.cos(i)
        z = y_op * math.sin(i)
        return x, y, z

    def eclipse_duration_s(self) -> float:
        """Approximate eclipse duration for LEO."""
        if self.altitude_periapsis_km() < 200:
            return 0.0
        # use cylindrical shadow model
        period = self.orbital_period_s()
        ratio = R_EARTH / self.semi_major_axis_m
        if ratio > 1.0:
            ratio = 1.0
        return period * (1.0 / math.pi) * math.asin(ratio)

    def j2_perturbation_raan_rad_s(self) -> float:
        """Rate of change of RAAN due to J2."""
        a = self.semi_major_axis_m
        e = self.eccentricity
        i = math.radians(self.inclination_deg)
        n = self.mean_motion_rad_s()
        return -1.5 * n * J2 * (R_EARTH / a) ** 2 * math.cos(i) / (1 - e ** 2) ** 2

    def report(self) -> dict:
        return {
            "period_min": self.orbital_period_s() / 60.0,
            "apoapsis_km": self.altitude_apoapsis_km(),
            "periapsis_km": self.altitude_periapsis_km(),
            "mean_motion_rad_s": self.mean_motion_rad_s(),
            "eclipse_min": self.eclipse_duration_s() / 60.0,
            "j2_raan_drift_deg_day": math.degrees(self.j2_perturbation_raan_rad_s()) * 86400.0,
        }


def circular_orbit(altitude_km: float, inclination_deg: float = 51.6) -> OrbitalElements:
    """Build circular orbital elements from altitude."""
    a = (R_EARTH + altitude_km * 1000.0)
    return OrbitalElements(
        semi_major_axis_m=a,
        eccentricity=0.0,
        inclination_deg=inclination_deg,
        raan_deg=0.0,
        arg_periapsis_deg=0.0,
        true_anomaly_deg=0.0,
    )


def hohmann_transfer(r1_km: float, r2_km: float) -> dict:
    """Compute Hohmann transfer dV between two circular orbits."""
    r1 = r1_km * 1000.0
    r2 = r2_km * 1000.0
    a_transfer = (r1 + r2) / 2.0
    v1 = math.sqrt(MU_EARTH / r1)
    v2 = math.sqrt(MU_EARTH / r2)
    v_peri = math.sqrt(MU_EARTH * (2.0 / r1 - 1.0 / a_transfer))
    v_apo = math.sqrt(MU_EARTH * (2.0 / r2 - 1.0 / a_transfer))
    dv1 = v_peri - v1
    dv2 = v2 - v_apo
    return {
        "dv1_m_s": dv1,
        "dv2_m_s": dv2,
        "total_dv_m_s": abs(dv1) + abs(dv2),
        "transfer_time_s": math.pi * math.sqrt(a_transfer ** 3 / MU_EARTH),
    }
