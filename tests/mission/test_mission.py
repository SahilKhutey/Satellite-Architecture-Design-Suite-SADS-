# SADS - Mission Timeline Verification
import pytest
from simulation.MissionTimeline import MissionTimeline

def test_mission_timeline_phases():
    timeline = MissionTimeline(
        satellite_name="SADS-Demo-1",
        phases=["Launch", "LEO Insertion", "Solar Array Deployment", "Payload Calibration", "Deorbit"]
    )
    assert timeline.satellite_name == "SADS-Demo-1"
    assert len(timeline.phases) == 5
    assert "Solar Array Deployment" in timeline.phases
