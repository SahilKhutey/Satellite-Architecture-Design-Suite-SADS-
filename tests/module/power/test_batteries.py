"""
SADS — Battery Module Tests
Cases P-101 to P-103
"""

import math
import pytest
from engines.power_mod.BatteryModel import Battery


class TestP101BatteryCapacity:
    """P-101: Battery capacity calculations."""

    def test_usable_capacity(self):
        bat = Battery(name="B", capacity_wh=100.0, dod_limit=0.30)
        assert math.isclose(bat.usable_capacity(), 30.0, rel_tol=1e-9)

    def test_energy_density(self):
        bat = Battery(name="B", capacity_wh=200.0, mass_kg=1.0)
        assert math.isclose(bat.energy_density(), 200.0)

    def test_zero_mass_density(self):
        bat = Battery(name="B", capacity_wh=200.0, mass_kg=0.0)
        assert bat.energy_density() == 0.0
