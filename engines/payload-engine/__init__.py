# SADS Payload Engine Package
from .payload_model import PayloadComponent, PayloadSystem
from .optical.optical_payload import OpticalPayloadModel
from .radar.radar_payload import RadarPayloadModel
from .communication.comm_payload import CommPayloadModel
from .science.science_payload import SciencePayloadModel

# Backward compatibility class
from dataclasses import dataclass
@dataclass
class OpticalPayload:
    name: str
    focal_length_m: float
    pixel_pitch_m: float = 5.5e-6

    def ground_sample_distance(self, altitude_km: float) -> float:
        """Calculate GSD in meters"""
        if self.focal_length_m <= 0:
            return float('inf')
        return (self.pixel_pitch_m * altitude_km * 1000.0) / self.focal_length_m

