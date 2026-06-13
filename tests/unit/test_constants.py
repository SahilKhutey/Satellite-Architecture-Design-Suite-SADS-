"""
SADS — Constants and Physical Unit Tests
Verify all physical constants match authoritative values.
"""

import math
import pytest
from engines.thermal_engine import STEFAN_BOLTZMANN
from engines.orbit_engine import MU_EARTH, R_EARTH
from engines.power_engine import SPEED_OF_LIGHT, SOLAR_FLUX_EARTH, EARTH_ALBEDO, INFRARED_EARTH

class TestPhysicalConstants:
    """All physical constants must match CODATA/JPL authoritative values."""

    def test_speed_of_light(self):
        """c = 299,792,458 m/s (exact)"""
        assert math.isclose(SPEED_OF_LIGHT, 299792458.0, rel_tol=1e-15)

    def test_earth_gravitational_parameter(self):
        """μ_Earth = 3.986004418e14 m³/s² (JPL DE440)"""
        # MU_EARTH in orbit_engine is already in m^3/s^2 (3.986004418e14)
        assert math.isclose(MU_EARTH, 3.986004418e14, rel_tol=1e-9)

    def test_earth_equatorial_radius(self):
        """R_Earth = 6,378,137.0 m (WGS-84)"""
        # R_EARTH in orbit_engine is already in meters (6378137.0)
        assert math.isclose(R_EARTH, 6378137.0, rel_tol=1e-9)

    def test_stefan_boltzmann(self):
        """σ = 5.670374419e-8 W/m²/K⁴ (CODATA 2018)"""
        assert math.isclose(STEFAN_BOLTZMANN, 5.670374419e-8, rel_tol=1e-12)

    def test_solar_constant(self):
        """S = 1361 W/m² at 1 AU"""
        assert math.isclose(SOLAR_FLUX_EARTH, 1361.0, rel_tol=1e-3)

    def test_earth_albedo(self):
        """Earth albedo ~0.30"""
        assert 0.25 < EARTH_ALBEDO < 0.35

    def test_earth_infrared(self):
        """Earth IR ~237 W/m²"""
        assert 220 < INFRARED_EARTH < 260
