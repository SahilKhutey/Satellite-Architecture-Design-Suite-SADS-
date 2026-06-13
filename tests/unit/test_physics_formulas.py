"""
SADS — Physics Formula Unit Tests
Direct closed-form checks of every physical law.
"""

import math
import pytest

class TestKeplerianMechanics:
    def test_keplers_third_law(self):
        """T² = (4π²/μ) a³"""
        from engines.orbit_mod import MU_EARTH
        a = 7000.0 * 1000.0  # Semimajor axis in meters (7000 km)
        T = 2 * math.pi * math.sqrt(a**3 / MU_EARTH)
        # T should be ~5828 s (~97 min)
        assert 5700 < T < 6000

    def test_vis_viva_circular(self):
        """v = √(μ/r) for circular orbit"""
        from engines.orbit_mod import MU_EARTH
        r = 7000.0 * 1000.0  # Radius in meters (7000 km)
        v = math.sqrt(MU_EARTH / r)  # m/s
        # v ~7546 m/s
        assert 7500 < v < 7600


class TestThermalPhysics:
    def test_stefan_boltzmann_blackbody(self):
        from engines.thermal_mod import Surface
        # Q = ε * σ * A * T⁴
        surf = Surface(name="Rad", area_m2=1.0, emissivity=0.85, absorptivity=0.2)
        q = surf.radiated_heat_w(300.0)
        # 0.85 * 5.67e-8 * 1.0 * 300^4 = 390.4 W
        assert 385 < q < 395


class TestPropulsion:
    def test_tsiolkovsky_exact(self):
        """ΔV = Isp × g₀ × ln(m₀/m_f)"""
        from engines.propulsion_mod import DeltaVCalculator
        dv = DeltaVCalculator.compute_dv(isp_s=300.0, m_dry=100.0, m_fuel=40.0)
        expected = 300.0 * 9.80665 * math.log(140.0 / 100.0)
        assert math.isclose(dv, expected, rel_tol=1e-6)


class TestCommunications:
    def test_free_space_path_loss(self):
        from engines.comm_mod import RFPropagation
        fspl_db = RFPropagation.path_loss_db(distance_km=1000.0, frequency_hz=8.4e9)
        # Path loss is exactly ~170.93 dB
        assert 170 < fspl_db < 172

    def test_parabolic_gain(self):
        from engines.comm_mod import Antenna
        ant = Antenna(diameter_m=1.0, frequency_hz=8.4e9, efficiency=0.55)
        g = ant.gain_dbi()
        # Gain is exactly ~36.295 dBi
        assert 35 < g < 38
