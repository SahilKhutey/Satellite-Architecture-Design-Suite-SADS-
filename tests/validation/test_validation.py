# SADS - Real Mission Validation
import pytest
import json

def test_validation_against_iss():
    # Compare circular orbit period with ISS reference dataset
    with open("tests/datasets/reference_missions.json") as f:
        data = json.load(f)
    iss_period = data["iss"]["period_min"]
    
    from engines.orbit_engine import circular_orbit
    orb = circular_orbit(data["iss"]["altitude_km"])
    period_min = orb.orbital_period_s() / 60.0
    
    # Must match historical ISS orbital period within 1%
    assert pytest.approx(period_min, rel=0.01) == iss_period
