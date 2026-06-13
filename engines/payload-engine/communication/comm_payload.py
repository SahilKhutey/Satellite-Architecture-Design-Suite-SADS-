# SADS Payload Engine - Communication Payload Model
from ..payload_model import PayloadComponent

class CommPayloadModel(PayloadComponent):
    def __init__(
        self, 
        name: str, 
        mass_kg: float, 
        nominal_power_w: float, 
        peak_power_w: float, 
        data_rate_bps: float,
        transponder_channels: int,
        channel_bandwidth_mhz: float
    ):
        super().__init__(name, "communication", mass_kg, nominal_power_w, peak_power_w, data_rate_bps)
        self.transponder_channels = transponder_channels
        self.channel_bandwidth_mhz = channel_bandwidth_mhz

    def total_bandwidth_mhz(self) -> float:
        return self.transponder_channels * self.channel_bandwidth_mhz

    def maximum_throughput_bps(self, spectral_efficiency_bps_hz: float = 2.0) -> float:
        """Throughput = Bandwidth * Spectral Efficiency"""
        return self.total_bandwidth_mhz() * 1e6 * spectral_efficiency_bps_hz
