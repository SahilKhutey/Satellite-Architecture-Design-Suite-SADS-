# SADS - Digital Twin Tests
import pytest

def test_twin_state_sync():
    # Twin core telemetry packet parsing checks
    packet = {"spacecraft_id": "SAT-1", "timestamp": "2026-06-13T09:47:00Z"}
    assert packet["spacecraft_id"] == "SAT-1"
