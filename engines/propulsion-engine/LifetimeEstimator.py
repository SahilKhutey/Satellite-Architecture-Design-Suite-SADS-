# SADS - Lifetime Estimator
class LifetimeEstimator:
    @staticmethod
    def estimate_years(fuel_mass: float, annual_burn_kg: float) -> float:
        if annual_burn_kg <= 0: return float('inf')
        return fuel_mass / annual_burn_kg
