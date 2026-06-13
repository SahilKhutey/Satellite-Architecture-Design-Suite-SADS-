# SADS Digital Twin Reference — Telemetry Framework

**Document ID:** SADS-TWN-TEL-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

The SADS Telemetry Ingestion framework supports parsing continuous streams of satellite telemetry frames.

---

## 2. Ingestion Format
Telemetry is ingested in JSON format:
```json
{
  "spacecraft_id": "SAT-1",
  "timestamp": "2026-06-13T09:47:00Z",
  "sensors": {
    "solar_panel_w": 250.0,
    "battery_soc": 0.85,
    "temp_k": 298.15
  }
}
```
If fields are missing, the ingestion system discards or flags the frame as invalid.
