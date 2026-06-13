# SADS Payload Engine - Scientific Payload Model
from ..payload_model import PayloadComponent

class SciencePayloadModel(PayloadComponent):
    def __init__(
        self, 
        name: str, 
        mass_kg: float, 
        nominal_power_w: float, 
        peak_power_w: float, 
        data_rate_bps: float,
        sensor_type: str = "spectrometer"
    ):
        super().__init__(name, "science", mass_kg, nominal_power_w, peak_power_w, data_rate_bps)
        self.sensor_type = sensor_type
