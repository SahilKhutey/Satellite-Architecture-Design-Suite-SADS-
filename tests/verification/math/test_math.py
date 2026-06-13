# SADS - Mathematics Verification
import pytest
import math

def test_differential_equations_solvers():
    # Verify analytical exponential decay y' = -k y vs numerical step
    k = 0.1
    y0 = 1.0
    dt = 0.1
    # Euler approximation: y1 = y0 - k*y0*dt
    y1_num = y0 - k * y0 * dt
    y1_anal = y0 * math.exp(-k * dt)
    # Should match closely for small time step
    assert math.isclose(y1_num, y1_anal, abs_tol=0.005)
