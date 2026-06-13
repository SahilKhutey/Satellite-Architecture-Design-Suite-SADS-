# SADS - Coverage Analyzer
class CoverageAnalyzer:
    @staticmethod
    def is_visible(sat_lat: float, sat_lon: float, gs_lat: float, gs_lon: float) -> bool:
        # Simple threshold check
        return abs(sat_lat - gs_lat) < 15.0 and abs(sat_lon - gs_lon) < 15.0
