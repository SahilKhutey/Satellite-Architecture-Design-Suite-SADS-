# SADS - Comm Module Tests
import pytest
from engines.comm_mod import Antenna, LinkBudget, RFPropagation, CoverageAnalyzer

def test_comm_pass():
    ant = Antenna(diameter_m=0.5, frequency_hz=8.4e9)
    gain = ant.gain_dbi()
    fspl = RFPropagation.path_loss_db(distance_km=1000.0, frequency_hz=8.4e9)
    margin = LinkBudget.calculate_margin(
        tx_power_w=5.0, tx_gain_db=15.0, rx_gain_db=gain,
        fspl_db=fspl, system_temp_k=290.0, data_rate_bps=1e6
    )
    assert margin > 0.0

def test_coverage():
    assert CoverageAnalyzer.is_visible(10.0, 20.0, 12.0, 22.0) is True
    assert CoverageAnalyzer.is_visible(10.0, 20.0, 50.0, 50.0) is False
