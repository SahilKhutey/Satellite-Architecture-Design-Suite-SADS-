# SADS - Comm Simulation
from .LinkBudget import LinkBudget
from .RFPropagation import RFPropagation

class CommSimulation:
    @staticmethod
    def simulate_pass(tx_power_w: float, freq_hz: float, dist_km: float) -> float:
        fspl = RFPropagation.path_loss_db(dist_km, freq_hz)
        return LinkBudget.calculate_margin(tx_power_w, 15.0, 30.0, fspl, 290.0, 1e6)
