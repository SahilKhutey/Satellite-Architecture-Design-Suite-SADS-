# SADS Payload Engine Unit Tests
import pytest
from engines.payload_engine import PayloadComponent, PayloadSystem
from engines.payload_engine import OpticalPayloadModel, RadarPayloadModel, CommPayloadModel, SciencePayloadModel

def test_optical_payload_resolution():
    opt = OpticalPayloadModel(
        name="Cam", mass_kg=15.0, nominal_power_w=10.0, peak_power_w=50.0, data_rate_bps=1e8,
        focal_length_m=1.2, aperture_diameter_m=0.3, pixel_pitch_m=5.5e-6
    )
    gsd = opt.ground_sample_distance(altitude_km=500.0)
    assert 2.0 < gsd < 2.5 # expected (5.5e-6 * 500e3) / 1.2 = 2.29m
    
    diff_limit = opt.spatial_resolution_limit_m(altitude_km=500.0)
    assert 1.0 < diff_limit < 1.5 # expected 1.22 * 550e-9 * 500e3 / 0.3 = 1.118m

def test_radar_payload_resolution():
    sar = RadarPayloadModel(
        name="Radar", mass_kg=120.0, nominal_power_w=50.0, peak_power_w=800.0, data_rate_bps=5e8,
        antenna_length_m=6.0, antenna_width_m=1.0, frequency_ghz=9.6
    )
    az_res = sar.azimuth_resolution_m()
    assert az_res == 3.0
    
    rng_res = sar.range_resolution_m(pulse_bandwidth_mhz=150.0)
    assert 0.9 < rng_res < 1.1

def test_payload_system_simulation():
    opt = OpticalPayloadModel(
        name="Cam", mass_kg=15.0, nominal_power_w=10.0, peak_power_w=50.0, data_rate_bps=1e8,
        focal_length_m=1.2, aperture_diameter_m=0.3
    )
    sys = PayloadSystem(payloads=[opt], buffer_capacity_bits=1e9)
    assert sys.get_total_mass() == 15.0
    assert sys.get_current_power_draw() == 10.0 # standby
    
    # Activate optical payload
    opt.state = "active"
    assert sys.get_current_power_draw() == 50.0
    
    # Simulate 10 seconds of active imaging with no downlink
    res = sys.simulate_step(dt_s=10.0, downlink_rate_bps=0.0)
    assert res["data_generated_bits"] == 1e9
    assert res["buffer_fill_bits"] == 1e9
    assert res["buffer_percent"] == 100.0
    assert res["buffer_overflow"] is True
