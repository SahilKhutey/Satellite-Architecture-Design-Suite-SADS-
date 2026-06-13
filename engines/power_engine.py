"""
SADS - Power Subsystem Engine
Models solar arrays, batteries, power distribution, and budgets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


# Physical constants
SOLAR_FLUX_EARTH = 1361.0  # W/m^2 (AM0)
EARTH_ALBEDO = 0.3
INFRARED_EARTH = 237.0  # W/m^2
SPEED_OF_LIGHT = 299792458.0  # m/s


@dataclass
class SolarArray:
    name: str
    area: float  # m^2
    efficiency: float = 0.30  # typical triple-junction GaAs
    degradation_per_year: float = 0.025
    cell_type: str = "triple-junction"
    years_in_service: float = 0.0

    def instantaneous_power(self, solar_flux: float = SOLAR_FLUX_EARTH) -> float:
        """P = eta * A * G"""
        deg = (1 - self.degradation_per_year) ** self.years_in_service
        return self.efficiency * self.area * solar_flux * deg


@dataclass
class Battery:
    name: str
    capacity_wh: float  # Watt-hours
    dod_limit: float = 0.30  # depth of discharge
    efficiency: float = 0.95
    mass_kg: float = 0.0
    cell_type: str = "Li-ion"

    def usable_capacity(self) -> float:
        return self.capacity_wh * self.dod_limit

    def energy_density(self) -> float:
        if self.mass_kg <= 0:
            return 0.0
        return self.capacity_wh / self.mass_kg


@dataclass
class Load:
    name: str
    nominal_power_w: float
    duty_cycle: float = 1.0  # fraction of orbit time active
    bus_voltage: float = 28.0

    def average_power(self) -> float:
        return self.nominal_power_w * self.duty_cycle


@dataclass
class PowerBudget:
    solar_arrays: List[SolarArray] = field(default_factory=list)
    batteries: List[Battery] = field(default_factory=list)
    loads: List[Load] = field(default_factory=list)
    eclipse_duration_min: float = 35.0  # typical LEO
    orbit_period_min: float = 95.0
    bus_voltage: float = 28.0

    def total_array_power(self, solar_flux: float = SOLAR_FLUX_EARTH) -> float:
        return sum(arr.instantaneous_power(solar_flux) for arr in self.solar_arrays)

    def average_load(self) -> float:
        return sum(load.average_power() for load in self.loads)

    def peak_load(self) -> float:
        return sum(load.nominal_power_w for load in self.loads)

    def total_battery_capacity(self) -> float:
        return sum(b.capacity_wh for b in self.batteries)

    def eclipse_energy_required(self) -> float:
        """Energy needed during eclipse (Wh)"""
        return self.average_load() * (self.eclipse_duration_min / 60.0)

    def battery_margin(self) -> float:
        """Returns (usable_capacity - required) / required"""
        required = self.eclipse_energy_required()
        if required == 0:
            return float('inf')
        usable = sum(b.usable_capacity() for b in self.batteries)
        return (usable - required) / required

    def power_balance(self, solar_flux: float = SOLAR_FLUX_EARTH) -> Dict[str, float]:
        gen = self.total_array_power(solar_flux)
        avg_load = self.average_load()
        peak = self.peak_load()
        eclipse_req = self.eclipse_energy_required()
        return {
            "generation_w": gen,
            "average_load_w": avg_load,
            "peak_load_w": peak,
            "generation_margin": (gen - avg_load) / avg_load if avg_load else 0.0,
            "eclipse_energy_wh": eclipse_req,
            "battery_capacity_wh": self.total_battery_capacity(),
            "battery_margin": self.battery_margin(),
            "status": "OK" if gen >= avg_load and self.battery_margin() >= 0 else "MARGINAL"
        }


def link_budget(freq_hz: float, tx_power_w: float, tx_gain_dbi: float,
                rx_gain_dbi: float, distance_km: float, data_rate_bps: float,
                system_temp_k: float = 300.0) -> Dict[str, float]:
    """Free-space link budget calculation."""
    lam = SPEED_OF_LIGHT / freq_hz
    d_m = distance_km * 1000.0
    fspl_db = 20 * math.log10(4 * math.pi * d_m / lam)
    bw_hz = data_rate_bps  # assume matched filter
    k = 1.380649e-23
    noise_db = 10 * math.log10(k * system_temp_k * bw_hz)
    eirp_db = 10 * math.log10(tx_power_w) + tx_gain_dbi
    c_n_db = eirp_db + rx_gain_dbi - fspl_db - noise_db
    c_n_linear = 10 ** (c_n_db / 10.0)
    return {
        "wavelength_m": lam,
        "free_space_loss_db": fspl_db,
        "noise_power_dbm": noise_db + 30,
        "eirp_dbm": eirp_db + 30,
        "cn_db": c_n_db,
        "cn_linear": c_n_linear,
        "cn_margin_db": c_n_db - 10.0,  # 10 dB threshold typical
    }
