# SADS Structures - Launch Loads Model
import math

class LaunchLoads:
    def __init__(self, static_g_axial: float = 6.0, dynamic_g_lateral: float = 2.0):
        self.static_g_axial = static_g_axial
        self.dynamic_g_lateral = dynamic_g_lateral

    def calculate_equivalent_acceleration(self) -> float:
        return math.sqrt(self.static_g_axial**2 + self.dynamic_g_lateral**2)

    def calculate_inertial_force_n(self, wet_mass_kg: float) -> float:
        g0 = 9.80665
        eq_g = self.calculate_equivalent_acceleration()
        return wet_mass_kg * eq_g * g0
