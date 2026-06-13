# Telemetry Models Reference

## 1. Frame Struct Layout
Telemetry streams are packetized as binary structures or JSON frames:
```json
{
  "timestamp": "2026-06-13T09:47:00Z",
  "spacecraft_id": "SADS-SAT-L1",
  "eps": {
    "voltage_v": 28.12,
    "current_a": 4.15,
    "battery_temp_k": 288.15
  },
  "adcs": {
    "quaternion": [0.0, 0.0, 0.0, 1.0],
    "angular_rates_rad_s": [0.001, -0.002, 0.0]
  }
}
```
## 2. Ingestion Storage
Stored in Postgres/TimescaleDB partition tables hypertable index key: `(timestamp, spacecraft_id)`.
