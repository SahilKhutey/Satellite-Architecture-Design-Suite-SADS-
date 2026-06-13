# SADS - Mission Simulation Tests
import pytest
from simulation.MissionSimulator import MissionSimulator

def test_simulation_timeline_evolution():
    sim = MissionSimulator()
    res = sim.run()
    assert "Simulation runs successfully." in res
