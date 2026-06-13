# SADS - Antenna Model
import math

class Antenna:
    def __init__(self, diameter_m: float, frequency_hz: float, efficiency: float = 0.55):
        self.diameter_m = diameter_m
        self.frequency_hz = frequency_hz
        self.efficiency = efficiency

    def gain_dbi(self) -> float:
        c = 299792458.0
        wavelength = c / self.frequency_hz
        gain = self.efficiency * (math.pi * self.diameter_m / wavelength) ** 2
        return 10 * math.log10(gain)
