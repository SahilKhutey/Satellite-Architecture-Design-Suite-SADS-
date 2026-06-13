# SADS - Thermal Validator
from .ThermalNetwork import ThermalNetwork

class ThermalValidator:
    @staticmethod
    def validate_temperatures(net: ThermalNetwork) -> bool:
        # Verifies all components stay in structural margins: e.g. [173 K, 373 K]
        for node in net.nodes:
            if not (150.0 < node.temperature_k < 400.0):
                return False
        return True
