# SADS - ADCS Module Tests
import pytest
from engines.adcs_mod import QuaternionMath, AttitudeSimulator, ADCSReport

def test_quaternion_normalization():
    q = [1.0, 2.0, 3.0, 4.0]
    q_norm = QuaternionMath.normalize(q)
    assert pytest.approx(sum(x*x for x in q_norm), abs=1e-9) == 1.0

def test_pointing_error():
    err = AttitudeSimulator.simulate_pointing_error(wheels_count=4)
    assert err < 0.05
    assert "degrees" in ADCSReport.generate(err)
