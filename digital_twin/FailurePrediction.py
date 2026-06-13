class FailurePrediction:
    @staticmethod
    def predict_remaining_lifetime_years(initial_efficiency: float, annual_degradation_rate: float, fail_threshold: float = 0.50) -> float:
        import math
        if annual_degradation_rate <= 0 or annual_degradation_rate >= 1:
            return 99.0
        ratio = fail_threshold / initial_efficiency
        if ratio >= 1.0:
            return 0.0
        return math.log(ratio) / math.log(1.0 - annual_degradation_rate)
