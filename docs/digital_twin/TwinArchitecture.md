# Digital Twin Architecture Reference

## 1. Synchronization Architecture
The SADS Digital Twin binds simulation engines with active physical satellite telemetry:
- **Telemetry Ingestion:** Receives actual sensor packets over gRPC or MQTT.
- **State Estimation:** Uses a Kalman Filter to align simulation node variables with noisy telemetry.
- **Predictive Mode:** Projects battery, propellant, and thermal trends to forecast future anomalies.

## 2. Broker Pipeline
Telemetry streams flow through Apache Kafka / MQTT brokers to database workers using TimescaleDB.
