# SADS - Thermal Report
from .ThermalNetwork import ThermalNetwork

class ThermalReport:
    @staticmethod
    def generate(net: ThermalNetwork) -> str:
        rep = "Thermal Analysis Nodal Temperatures:\n"
        for n in net.nodes:
            rep += f"Node: {n.name:<15} Temp: {n.temperature_k:.1f} K ({n.temperature_k - 273.15:.1f} C)\n"
        return rep
