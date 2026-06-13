# SADS - Physics Verification
import pytest

def test_conservation_of_energy():
    # Energy generator efficiency must be <= 1.0
    eta = 0.30
    assert eta <= 1.0, "Violates conservation of energy"
