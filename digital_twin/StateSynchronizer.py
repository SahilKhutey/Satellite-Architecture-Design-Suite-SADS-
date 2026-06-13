# SADS - State Synchronizer
class StateSynchronizer:
    @staticmethod
    def filter_step(estimated_value: float, measured_value: float, gain: float = 0.1) -> float:
        # steady-state filter update step
        return estimated_value + gain * (measured_value - estimated_value)
