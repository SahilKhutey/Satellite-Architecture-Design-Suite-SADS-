# SADS - Orbit Transfer
import math

class OrbitTransfer:
    @staticmethod
    def hohmann(r1_km: float, r2_km: float, mu: float = 398600.4418) -> dict:
        v1 = math.sqrt(mu / r1_km)
        v2 = math.sqrt(mu / r2_km)
        dv1 = v1 * (math.sqrt(2 * r2_km / (r1_km + r2_km)) - 1.0)
        dv2 = v2 * (1.0 - math.sqrt(2 * r1_km / (r1_km + r2_km)))
        return {"dv1": dv1 * 1000.0, "dv2": dv2 * 1000.0, "total_dv": (dv1 + dv2) * 1000.0}
