# SADS - Orbit Report
class OrbitReport:
    @staticmethod
    def generate(alt: float) -> str:
        r_earth = 6378.137
        return f"Orbit Altitude: {alt} km (Semimajor axis: {alt + r_earth:.3f} km)"
