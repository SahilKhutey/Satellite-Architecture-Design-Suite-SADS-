# SADS - J2 Perturbation Model
import math

class J2Perturbation:
    @staticmethod
    def precession_rates(a: float, e: float, i: float) -> tuple:
        r_earth = 6378.137
        j2 = 1.08263e-3
        mu = 398600.4418
        p = a * (1 - e**2)
        n = math.sqrt(mu / a**3)
        raan_rate = -1.5 * j2 * (r_earth / p)**2 * n * math.cos(i)
        arg_pe_rate = 0.75 * j2 * (r_earth / p)**2 * n * (4 - 5 * (math.sin(i)**2))
        return raan_rate, arg_pe_rate
