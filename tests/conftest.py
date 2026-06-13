"""
SADS — Pytest Configuration and Shared Fixtures.

Provides reusable fixtures, test data, and configuration for the entire
SADS test suite.
"""

import pytest
import json
import math
import os
from pathlib import Path
from typing import Dict, Any

# Test data paths
DATASETS_DIR = Path(__file__).parent / "datasets"


# ===== General Configuration =====
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Pure function unit tests")
    config.addinivalue_line("markers", "module: Module-level tests")
    config.addinivalue_line("markers", "subsystem: Subsystem tests")
    config.addinivalue_line("markers", "integration: Cross-engine integration")
    config.addinivalue_line("markers", "simulation: Mission simulations")
    config.addinivalue_line("markers", "verification: Math/physics/engineering verification")
    config.addinivalue_line("markers", "validation: Real mission validation")
    config.addinivalue_line("markers", "mission: Mission scenario tests")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "regression: Regression/snapshot tests")
    config.addinivalue_line("markers", "acceptance: Acceptance criteria")
    config.addinivalue_line("markers", "twin: Digital twin tests")
    config.addinivalue_line("markers", "ai: AI Copilot tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "physics: Physics verification")
    config.addinivalue_line("markers", "math: Math verification")
    config.addinivalue_line("markers", "engineering: Engineering verification")


# ===== Common Fixtures =====

@pytest.fixture
def reference_mission_data() -> Dict[str, Any]:
    """Load reference mission data for validation."""
    return {
        "iss": {
            "altitude_km": 408,
            "inclination_deg": 51.6,
            "period_min": 92.68,
            "eccentricity": 0.0001,
        },
        "hubble": {
            "altitude_km": 540,
            "inclination_deg": 28.5,
            "period_min": 95.42,
        },
        "gps_block_iiia": {
            "altitude_km": 20200,
            "inclination_deg": 55.0,
            "period_h": 11.97,
        },
        "geo": {
            "altitude_km": 35786,
            "period_h": 23.93,
            "inclination_deg": 0.0,
        },
        "starlink": {
            "altitude_km": 550,
            "inclination_deg": 53.0,
            "period_min": 95.6,
        },
    }


@pytest.fixture
def cubesat_3u() -> Dict[str, Any]:
    """3U CubeSat reference configuration."""
    return {
        "mass_kg": 4.0,
        "volume_l": 3.4,
        "dimensions_mm": {"x": 100, "y": 100, "z": 340.5},
        "solar_array_area_m2": 0.10,
        "battery_capacity_wh": 30.0,
        "average_load_w": 4.0,
        "peak_load_w": 8.0,
        "altitude_km": 500,
        "inclination_deg": 97.6,  # SSO
    }


@pytest.fixture
def geo_comsat() -> Dict[str, Any]:
    """GEO communications satellite reference."""
    return {
        "dry_mass_kg": 2000,
        "altitude_km": 35786,
        "eclipse_season_days": 90,  # per year
        "max_eclipse_min": 72,  # longest eclipse
        "mission_years": 15,
        "battery_capacity_kwh": 5.0,
        "average_load_w": 2500,
        "peak_load_w": 4000,
    }


@pytest.fixture
def mars_orbiter() -> Dict[str, Any]:
    """Mars orbiter reference."""
    return {
        "dry_mass_kg": 800,
        "xenon_kg": 200,
        "heliocentric_dv_m_s": 3600,
        "mars_orbit_insertion_dv_m_s": 1100,
        "primary_instrument": "high_res_camera",
    }


@pytest.fixture
def numerical_tolerances():
    """Numerical tolerances used throughout tests."""
    return {
        "absolute_strict": 1e-12,
        "absolute_default": 1e-9,
        "absolute_loose": 1e-6,
        "relative_strict": 1e-9,
        "relative_default": 1e-6,
        "relative_loose": 1e-3,
        "energy_conservation": 1e-7,
        "angle_arcsec": 1.0,
    }


@pytest.fixture
def component_library_data():
    """Load component library test data."""
    lib_path = Path(__file__).parent.parent / "libraries" / "components" / "library.json"
    if lib_path.exists():
        with open(lib_path) as f:
            return json.load(f)
    return {"components": {}, "satellites": {}}


# ===== Physics Constants =====
@pytest.fixture
def physics_constants():
    """Standard physical constants used in tests."""
    return {
        "MU_EARTH": 3.986004418e14,  # m³/s²
        "R_EARTH": 6378137.0,  # m
        "G0": 9.80665,  # m/s²
        "C": 299792458.0,  # m/s
        "K_BOLTZMANN": 1.380649e-23,  # J/K
        "STEFAN_BOLTZMANN": 5.670374419e-8,  # W/m²/K⁴
        "SOLAR_FLUX": 1361.0,  # W/m²
        "AU": 1.495978707e11,  # m
        "J2": 1.08263e-3,
    }


# ===== Tolerance Assertions =====
def assert_close(actual, expected, abs_tol=1e-9, rel_tol=1e-9, msg=""):
    """Assert with detailed error message."""
    if not math.isclose(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol):
        raise AssertionError(
            f"{msg}: expected {expected}, got {actual} "
            f"(abs_tol={abs_tol}, rel_tol={rel_tol})"
        )


# ===== Custom Skip Markers =====
def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --runslow is set."""
    if not config.getoption("--runslow", default=False):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="Run slow tests"
    )
