# SADS Payload Engine - SAR Radar Payload Model
import math
from ..payload_model import PayloadComponent

class RadarPayloadModel(PayloadComponent):
    def __init__(
        self, 
        name: str, 
        mass_kg: float, 
        nominal_power_w: float, 
        peak_power_w: float, 
        data_rate_bps: float,
        antenna_length_m: float,
        antenna_width_m: float,
        frequency_ghz: float = 9.6  # X-band typical
    ):
        super().__init__(name, "radar", mass_kg, nominal_power_w, peak_power_w, data_rate_bps)
        self.antenna_length_m = antenna_length_m
        self.antenna_width_m = antenna_width_m
        self.frequency_hz = frequency_ghz * 1e9
        self.speed_of_light = 299792458.0
        self.wavelength_m = self.speed_of_light / self.frequency_hz

    def azimuth_resolution_m(self) -> float:
        """For SAR, theoretical azimuth resolution is antenna_length / 2"""
        return self.antenna_length_m / 2.0

    def range_resolution_m(self, pulse_bandwidth_mhz: float = 100.0) -> float:
        """c / (2 * B)"""
        return self.speed_of_light / (2.0 * pulse_bandwidth_mhz * 1e6)
