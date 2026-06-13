# SADS - Link Budget Solver
import math

class LinkBudget:
    @staticmethod
    def calculate_margin(tx_power_w: float, tx_gain_db: float, rx_gain_db: float, fspl_db: float, system_temp_k: float, data_rate_bps: float) -> float:
        k_b = 1.380649e-23
        noise_power = k_b * system_temp_k * data_rate_bps
        noise_db = 10 * math.log10(noise_power)
        eirp_db = 10 * math.log10(tx_power_w) + tx_gain_db
        cn_db = eirp_db + rx_gain_db - fspl_db - noise_db
        return cn_db - 10.0  # 10 dB threshold
