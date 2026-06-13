"""
SADS — Solar Panel Module Tests
Cases P-001 to P-005
"""

import math
import pytest
from engines.power_mod.SolarPanelModel import SolarArray


class TestP001SolarGeneration:
    """P-001: Power generation during sunlight."""

    def test_power_positive_in_sunlight(self):
        arr = SolarArray(name="SA", area=1.0, efficiency=0.30)
        p = arr.instantaneous_power()
        assert p > 0, "Solar array must produce power in sunlight"

    def test_power_proportional_to_area(self):
        arr1 = SolarArray(name="A1", area=1.0, efficiency=0.30)
        arr2 = SolarArray(name="A2", area=2.0, efficiency=0.30)
        p1 = arr1.instantaneous_power()
        p2 = arr2.instantaneous_power()
        assert math.isclose(p2 / p1, 2.0, rel_tol=1e-6)

    def test_zero_power_at_zero_flux(self):
        arr = SolarArray(name="SA", area=1.0, efficiency=0.30)
        p = arr.instantaneous_power(solar_flux=0.0)
        assert p == 0


class TestP002Degradation:
    """P-002: Solar array degradation over time."""

    def test_bol_equals_year_zero(self):
        arr = SolarArray(name="SA", area=1.0, efficiency=0.30,
                         degradation_per_year=0.025, years_in_service=0.0)
        p = arr.instantaneous_power()
        assert math.isclose(p, 0.30 * 1.0 * 1361.0, rel_tol=1e-6)

    def test_decreases_over_time(self):
        arr = SolarArray(name="SA", area=1.0, efficiency=0.30, degradation_per_year=0.025)
        p0 = arr.instantaneous_power()
        arr.years_in_service = 5.0
        p5 = arr.instantaneous_power()
        assert p5 < p0
