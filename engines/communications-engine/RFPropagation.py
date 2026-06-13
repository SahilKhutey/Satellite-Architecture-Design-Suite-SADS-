# SADS - RF Propagation Model
import math

class RFPropagation:
    @staticmethod
    def path_loss_db(distance_km: float, frequency_hz: float) -> float:
        c = 299792458.0
        lam = c / frequency_hz
        return 20 * math.log10(4 * math.pi * (distance_km * 1000.0) / lam)
