from typing import List

class TwinAnalytics:
    @staticmethod
    def calculate_average(values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def calculate_trend(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        return (values[-1] - values[0]) / float(len(values) - 1)
