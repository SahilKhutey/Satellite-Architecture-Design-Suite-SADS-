# SADS - Thermal Solver
import math
from .ThermalNetwork import ThermalNetwork
from .RadiationModel import SIGMA

class ThermalSolver:
    @staticmethod
    def solve_equilibrium(net: ThermalNetwork, solar_flux: float = 1361.0, max_iter: int = 100, tol: float = 1e-5) -> None:
        # Simple Newton-Raphson solver for 1-node or uncoupled nodes
        for node in net.nodes:
            T = node.temperature_k
            q_ext = node.total_external_heat_w(solar_flux)
            q_int = node.internal_heat_w + node.total_heaters_heat_w()
            
            # Radiative area sum
            sum_e_a = sum(s.emissivity * s.area_m2 for s in node.surfaces)
            if sum_e_a <= 0:
                continue

            for _ in range(max_iter):
                f = q_ext + q_int - sum_e_a * SIGMA * (T ** 4)
                df = -4.0 * sum_e_a * SIGMA * (T ** 3)
                if abs(df) < 1e-12:
                    break
                dT = f / df
                T -= dT
                if abs(dT) < tol:
                    break
            node.temperature_k = T
