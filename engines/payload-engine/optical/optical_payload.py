# SADS Payload Engine - Optical Payload Model
import math
from ..payload_model import PayloadComponent

class OpticalPayloadModel(PayloadComponent):
    def __init__(
        self, 
        name: str, 
        mass_kg: float, 
        nominal_power_w: float, 
        peak_power_w: float, 
        data_rate_bps: float,
        focal_length_m: float,
        aperture_diameter_m: float,
        pixel_pitch_m: float = 5.5e-6,
        wavelength_nm: float = 550.0
    ):
        super().__init__(name, "optical", mass_kg, nominal_power_w, peak_power_w, data_rate_bps)
        self.focal_length_m = focal_length_m
        self.aperture_diameter_m = aperture_diameter_m
        self.pixel_pitch_m = pixel_pitch_m
        self.wavelength_m = wavelength_nm * 1e-9

    def ground_sample_distance(self, altitude_km: float) -> float:
        """GSD = (pixel_pitch * altitude) / focal_length"""
        if self.focal_length_m <= 0:
            return float('inf')
        return (self.pixel_pitch_m * altitude_km * 1000.0) / self.focal_length_m

    def spatial_resolution_limit_m(self, altitude_km: float) -> float:
        """Diffraction limit: res = 1.22 * lambda * altitude / aperture"""
        if self.aperture_diameter_m <= 0:
            return float('inf')
        return 1.22 * self.wavelength_m * (altitude_km * 1000.0) / self.aperture_diameter_m
