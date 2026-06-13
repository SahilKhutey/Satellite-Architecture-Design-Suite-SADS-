"""
SADS — Eclipse Analysis Module Tests
"""

import math
import pytest
from engines.power_mod.EclipseAnalyzer import EclipseAnalyzer


class TestEclipseDuration:
    def test_leo_500km(self):
        duration = EclipseAnalyzer.calculate_eclipse_duration(altitude_km=500.0)
        # LEO 500km eclipse duration is typically ~35 min
        assert 30.0 < duration < 40.0

    def test_geo_eclipse(self):
        duration = EclipseAnalyzer.calculate_eclipse_duration(altitude_km=35786.0)
        # GEO equinox eclipse duration is typically ~72 min
        assert 65.0 < duration < 75.0
