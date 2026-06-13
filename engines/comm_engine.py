"""
SADS - Communication Subsystem Engine
RF link budgets, antenna gain, SNR/BER estimation.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


SPEED_OF_LIGHT = 299792458.0
BOLTZMANN = 1.380649e-23


@dataclass
class Antenna:
    name: str = "Antenna"
    diameter_m: float = 0.0
    frequency_hz: float = 8.4e9  # X-band default
    efficiency: float = 0.55
    polarization_loss_db: float = 0.5

    def gain_dbi(self) -> float:
        """G = eta * (pi*D/lambda)^2"""
        lam = SPEED_OF_LIGHT / self.frequency_hz
        g_linear = self.efficiency * (math.pi * self.diameter_m / lam) ** 2
        return 10 * math.log10(g_linear) if g_linear > 0 else 0.0

    def beamwidth_deg(self) -> float:
        lam = SPEED_OF_LIGHT / self.frequency_hz
        if self.diameter_m == 0:
            return 180.0
        return 70.0 * lam / self.diameter_m


@dataclass
class Transmitter:
    name: str = "Transmitter"
    power_w: float = 5.0
    line_loss_db: float = 1.0
    data_rate_bps: float = 1e6


@dataclass
class Receiver:
    name: str = "Receiver"
    system_temp_k: float = 350.0
    required_cn_db: float = 10.0
    implementation_loss_db: float = 1.5


@dataclass
class LinkBudget:
    tx: Transmitter
    rx_antenna: Antenna
    receiver: Receiver
    distance_km: float = 600.0
    atmospheric_loss_db: float = 1.0
    rain_margin_db: float = 0.0

    def compute(self) -> Dict[str, float]:
        lam = SPEED_OF_LIGHT / self.rx_antenna.frequency_hz
        d_m = self.distance_km * 1000.0
        fspl_db = 20 * math.log10(4 * math.pi * d_m / lam)
        eirp_db = 10 * math.log10(self.tx.power_w) + self.rx_antenna.gain_dbi() - self.tx.line_loss_db
        noise_dbw = 10 * math.log10(BOLTZMANN * self.receiver.system_temp_k * self.tx.data_rate_bps)
        
        # convert to dB-Hz based formulation
        c_n_db = eirp_db - fspl_db - self.atmospheric_loss_db - self.rain_margin_db - self.receiver.implementation_loss_db - self.rx_antenna.polarization_loss_db - noise_dbw
        margin = c_n_db - self.receiver.required_cn_db
        return {
            "wavelength_m": lam,
            "free_space_loss_db": fspl_db,
            "eirp_dbw": eirp_db,
            "noise_dbw": noise_dbw,
            "cn_ratio_db": c_n_db,
            "required_cn_db": self.receiver.required_cn_db,
            "link_margin_db": margin,
            "link_closed": margin > 0,
            "beamwidth_deg": self.rx_antenna.beamwidth_deg(),
        }


def ber_from_ebn0(eb_n0_db: float, modulation: str = "BPSK") -> float:
    """Approximate BER from Eb/N0."""
    eb_n0 = 10 ** (eb_n0_db / 10.0)
    if modulation.upper() == "BPSK":
        return 0.5 * math.erfc(math.sqrt(eb_n0))
    elif modulation.upper() == "QPSK":
        return 0.5 * math.erfc(math.sqrt(eb_n0 / 2.0))
    return 0.5 * math.erfc(math.sqrt(eb_n0))
