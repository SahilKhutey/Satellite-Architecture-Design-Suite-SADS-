# SADS - Atmospheric Drag Model
class DragModel:
    @staticmethod
    def force(rho: float, cd: float, area: float, vel: list) -> list:
        v_mag = sum(x*x for x in vel) ** 0.5
        factor = -0.5 * rho * cd * area * v_mag
        return [factor * x for x in vel]
