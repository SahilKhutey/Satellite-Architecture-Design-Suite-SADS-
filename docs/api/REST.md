# SADS — API Specification

**Document ID:** SADS-API-001
**Revision:** 1.0

---

## 1. REST API Overview

SADS exposes a stateless REST API running on FastAPI. It serves design configurations, runs simulations, and returns engineering margins.

* **Base URL:** `/api`
* **Default Port:** `8000`
* **Content-Type:** `application/json`

---

## 2. API Endpoints

### 2.1 Power Subsystem Analyzer
* **Endpoint:** `POST /api/power/analyze`
* **Request Schema:**
```json
{
  "arrays": [
    {
      "name": "GaAs Panel Left",
      "area": 1.5,
      "efficiency": 0.30,
      "degradation_per_year": 0.025
    }
  ],
  "batteries": [
    {
      "name": "Li-ion Pack 1",
      "capacity_wh": 120.0,
      "dod_limit": 0.30,
      "mass_kg": 3.0
    }
  ],
  "loads": [
    {
      "name": "Avionics Load",
      "nominal_power_w": 25.0,
      "duty_cycle": 1.0
    }
  ],
  "eclipse_duration_min": 35.0,
  "orbit_period_min": 93.0
}
```
* **Response Schema:**
```json
{
  "generation_w": 612.45,
  "average_load_w": 25.0,
  "peak_load_w": 25.0,
  "generation_margin": 23.498,
  "eclipse_energy_wh": 14.5833,
  "battery_capacity_wh": 120.0,
  "battery_margin": 1.468,
  "status": "OK"
}
```

### 2.2 Thermal Subsystem Analyzer
* **Endpoint:** `POST /api/thermal/analyze`
* **Request Schema:**
```json
{
  "nodes": [
    {
      "name": "Spacecraft Bus",
      "mass_kg": 75.0,
      "specific_heat_j_kg_k": 900.0,
      "internal_heat_w": 50.0,
      "temperature_k": 300.0,
      "surfaces": [
        {
          "name": "Radiator Face",
          "area_m2": 0.8,
          "absorptivity": 0.20,
          "emissivity": 0.85
        }
      ],
      "heaters": []
    }
  ]
}
```
* **Response Schema:**
```json
{
  "Spacecraft Bus": {
    "temperature_k": 281.34,
    "temperature_c": 8.19,
    "heat_in_w": 182.44,
    "heat_out_w": 182.44,
    "heater_power_w": 0.0,
    "margin_ok": true
  }
}
```

### 2.3 Communications Analyzer
* **Endpoint:** `POST /api/comm/analyze`
* **Request Schema:**
```json
{
  "tx_power_w": 5.0,
  "tx_line_loss_db": 1.0,
  "data_rate_bps": 1000000.0,
  "rx_diameter_m": 0.5,
  "rx_frequency_hz": 8400000000.0,
  "rx_efficiency": 0.55,
  "distance_km": 1000.0,
  "system_temp_k": 290.0,
  "required_cn_db": 10.0,
  "atmospheric_loss_db": 1.0
}
```
* **Response Schema:**
```json
{
  "wavelength_m": 0.03569,
  "free_space_loss_db": 170.92,
  "eirp_dbw": 34.275,
  "noise_dbw": -144.38,
  "cn_ratio_db": 25.43,
  "required_cn_db": 10.0,
  "link_margin_db": 15.43,
  "link_closed": true,
  "beamwidth_deg": 4.99
}
```

### 2.4 Simulation Run Orchestrator
* **Endpoint:** `POST /api/simulation/run`
* **Request Schema:**
Combines `power`, `thermal`, `propulsion`, and `orbit` parameters inside a single payload along with a set of `phases` (MissionTimeline).
* **Response Schema:**
```json
{
  "satellite": "EagleEye-1",
  "mission_duration_days": 0.06,
  "total_energy_wh": 172.8,
  "power": { ... },
  "thermal": { ... },
  "propulsion": { ... },
  "orbit": { ... },
  "feasibility": {
    "power_ok": true,
    "thermal_ok": true,
    "propulsion_ok": true
  }
}
```

### 2.5 COTS Hardware Catalog
* **Endpoint:** `GET /api/components/library`
* **Response:** Returns the structured JSON database of solar panels, batteries, thrusters, antennas, reaction wheels, and sensors.
