# SADS - Maneuver Engine
class ManeuverEngine:
    @staticmethod
    def apply_impulse(vel: list, dv: list) -> list:
        return [v + d for v, d in zip(vel, dv)]
