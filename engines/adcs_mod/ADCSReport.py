# SADS - ADCS Report
class ADCSReport:
    @staticmethod
    def generate(error: float) -> str:
        return f"Pointing Accuracy Error: {error:.4f} degrees"
