# SADS - Comm Report
class CommReport:
    @staticmethod
    def generate(margin: float) -> str:
        return f"RF Link Budget Margin: {margin:.2f} dB (Status: {'OK' if margin >= 3.0 else 'UNSTABLE'})"
