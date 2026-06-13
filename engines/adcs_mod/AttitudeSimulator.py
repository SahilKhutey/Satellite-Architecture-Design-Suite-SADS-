# SADS - Attitude Simulator
class AttitudeSimulator:
    @staticmethod
    def simulate_pointing_error(wheels_count: int) -> float:
        # Base pointing error
        return 0.05 / (wheels_count if wheels_count > 0 else 1)
